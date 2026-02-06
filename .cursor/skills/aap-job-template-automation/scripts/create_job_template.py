#!/usr/bin/env python3
"""
AAP Job Template Creator

Creates an AAP job template from an Ansible playbook, automatically
generating surveys from playbook variables.
"""

import argparse
import json
import os
import sys
import yaml
import re
from typing import Dict, List, Any, Optional
import requests
from requests.auth import HTTPBasicAuth


class AAPClient:
    """Client for interacting with AAP API"""
    
    def __init__(self):
        self.hostname = os.getenv('AAP_HOSTNAME')
        self.username = os.getenv('AAP_USERNAME')
        self.password = os.getenv('AAP_PASSWORD')
        self.token = os.getenv('AAP_TOKEN')
        
        if not self.hostname:
            raise ValueError("AAP_HOSTNAME environment variable is required")
        
        if not self.token and not (self.username and self.password):
            raise ValueError("Either AAP_TOKEN or both AAP_USERNAME and AAP_PASSWORD are required")
        
        # Remove trailing slash from hostname
        self.hostname = self.hostname.rstrip('/')
        self.base_url = f"{self.hostname}/api/v2"
        
        # Set up authentication
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
        else:
            self.session.auth = HTTPBasicAuth(self.username, self.password)
        
        # Disable SSL warnings if needed (not recommended for production)
        self.session.verify = True
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to AAP API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict) -> Dict:
        """Make POST request to AAP API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def patch(self, endpoint: str, data: Dict) -> Dict:
        """Make PATCH request to AAP API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.patch(url, json=data)
        response.raise_for_status()
        return response.json()


class PlaybookParser:
    """Parse Ansible playbooks to extract metadata and variables"""
    
    @staticmethod
    def parse_playbook(playbook_path: str) -> Dict[str, Any]:
        """Parse playbook and extract relevant information"""
        with open(playbook_path, 'r') as f:
            content = f.read()
            
        # Parse YAML
        try:
            playbook = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse playbook YAML: {e}")
        
        if not playbook or not isinstance(playbook, list) or len(playbook) == 0:
            raise ValueError("Playbook must contain at least one play")
        
        # Get the first play
        play = playbook[0]
        
        # Extract play name
        play_name = play.get('name', 'Unnamed Playbook')
        
        # Extract variables with comments
        variables = PlaybookParser._extract_variables_with_comments(content, play)
        
        return {
            'name': play_name,
            'variables': variables,
            'hosts': play.get('hosts', 'all'),
            'become': play.get('become', False)
        }
    
    @staticmethod
    def _extract_variables_with_comments(content: str, play: Dict) -> List[Dict[str, Any]]:
        """Extract variables with their comments from playbook"""
        variables = []
        vars_dict = play.get('vars', {})
        
        if not vars_dict:
            return variables
        
        # Split content into lines for comment extraction
        lines = content.split('\n')
        
        for var_name, var_value in vars_dict.items():
            # Find the line with this variable
            comment = None
            for i, line in enumerate(lines):
                if re.search(rf'^\s*{re.escape(var_name)}\s*:', line):
                    # Look for comment on previous line or same line
                    if i > 0:
                        prev_line = lines[i - 1].strip()
                        if prev_line.startswith('#'):
                            comment = prev_line.lstrip('#').strip()
                    
                    # Check for inline comment
                    if '#' in line:
                        inline_comment = line.split('#', 1)[1].strip()
                        comment = inline_comment or comment
                    break
            
            # Determine variable type
            var_type = PlaybookParser._get_variable_type(var_value)
            
            variables.append({
                'name': var_name,
                'default': var_value,
                'type': var_type,
                'description': comment or f"Variable: {var_name}"
            })
        
        return variables
    
    @staticmethod
    def _get_variable_type(value: Any) -> str:
        """Determine survey field type from variable value"""
        if isinstance(value, bool):
            return 'multiplechoice'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, list):
            return 'multiselect' if len(value) < 10 else 'textarea'
        else:
            return 'text'


class JobTemplateCreator:
    """Create AAP job templates with surveys"""
    
    def __init__(self, client: AAPClient):
        self.client = client
    
    def create_job_template(
        self,
        name: str,
        playbook: str,
        project_name: str,
        inventory_name: str = None,
        variables: List[Dict] = None,
        **kwargs
    ) -> Dict:
        """Create a job template in AAP"""
        
        # Get project ID
        projects = self.client.get('/projects/', params={'name': project_name})
        if projects['count'] == 0:
            raise ValueError(f"Project '{project_name}' not found in AAP")
        project_id = projects['results'][0]['id']
        
        # Get inventory ID (use default if not specified)
        if inventory_name:
            inventories = self.client.get('/inventories/', params={'name': inventory_name})
            if inventories['count'] == 0:
                raise ValueError(f"Inventory '{inventory_name}' not found in AAP")
            inventory_id = inventories['results'][0]['id']
        else:
            # Try to find a default inventory
            inventories = self.client.get('/inventories/')
            if inventories['count'] == 0:
                raise ValueError("No inventories found in AAP. Please specify --inventory")
            inventory_id = inventories['results'][0]['id']
            print(f"Using inventory: {inventories['results'][0]['name']}")
        
        # Create job template
        template_data = {
            'name': name,
            'job_type': 'run',
            'inventory': inventory_id,
            'project': project_id,
            'playbook': playbook,
            'ask_variables_on_launch': True,
            **kwargs
        }
        
        print(f"Creating job template '{name}'...")
        try:
            template = self.client.post('/job_templates/', template_data)
            print(f"✓ Job template created successfully (ID: {template['id']})")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400 and 'already exists' in str(e.response.content):
                print(f"Job template '{name}' already exists, updating...")
                # Get existing template
                templates = self.client.get('/job_templates/', params={'name': name})
                template = templates['results'][0]
                # Update it
                self.client.patch(f"/job_templates/{template['id']}/", template_data)
                print(f"✓ Job template updated successfully (ID: {template['id']})")
            else:
                raise
        
        # Create survey if variables exist
        if variables:
            self._create_survey(template['id'], variables)
        
        return template
    
    def _create_survey(self, template_id: int, variables: List[Dict]):
        """Create a survey for the job template"""
        survey_spec = {
            'name': 'Playbook Variables',
            'description': 'Configure playbook variables',
            'spec': []
        }
        
        for var in variables:
            question = {
                'question_name': var['description'],
                'question_description': f"Variable: {var['name']}",
                'variable': var['name'],
                'type': var['type'],
                'required': False
            }
            
            # Set default value
            if var['type'] == 'multiplechoice':
                question['choices'] = ['true', 'false']
                question['default'] = str(var['default']).lower()
            elif var['type'] == 'multiselect':
                if isinstance(var['default'], list):
                    question['choices'] = '\n'.join(str(x) for x in var['default'])
                    question['default'] = var['default'][0] if var['default'] else ''
            else:
                question['default'] = str(var['default'])
            
            survey_spec['spec'].append(question)
        
        print(f"Creating survey with {len(variables)} variables...")
        self.client.post(f"/job_templates/{template_id}/survey_spec/", survey_spec)
        
        # Enable the survey
        self.client.patch(f"/job_templates/{template_id}/", {'survey_enabled': True})
        print(f"✓ Survey created and enabled")


def main():
    parser = argparse.ArgumentParser(
        description='Create AAP job template from Ansible playbook'
    )
    parser.add_argument(
        'playbook',
        help='Path to the Ansible playbook file'
    )
    parser.add_argument(
        '--project',
        default='ai-hacking',
        help='AAP project name (default: ai-hacking)'
    )
    parser.add_argument(
        '--inventory',
        help='AAP inventory name (if not specified, uses first available)'
    )
    parser.add_argument(
        '--update',
        action='store_true',
        help='Update existing job template if it exists'
    )
    
    args = parser.parse_args()
    
    # Verify playbook exists
    if not os.path.exists(args.playbook):
        print(f"Error: Playbook file '{args.playbook}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse playbook
        print(f"Parsing playbook: {args.playbook}")
        playbook_info = PlaybookParser.parse_playbook(args.playbook)
        print(f"✓ Playbook name: {playbook_info['name']}")
        print(f"✓ Found {len(playbook_info['variables'])} variables")
        
        # Create AAP client
        client = AAPClient()
        
        # Create job template
        creator = JobTemplateCreator(client)
        template = creator.create_job_template(
            name=playbook_info['name'],
            playbook=os.path.basename(args.playbook),
            project_name=args.project,
            inventory_name=args.inventory,
            variables=playbook_info['variables']
        )
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Job template '{playbook_info['name']}' is ready to use")
        print(f"View in AAP: {client.hostname}/#/templates/job_template/{template['id']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
