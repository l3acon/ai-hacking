"""
Ansible filter plugin: playbook_to_job_template

Parses playbook content and returns an AAP Config as Code job template
definition with auto-generated survey from playbook variables.

Usage in a playbook:
  vars:
    job_template: >-
      {{ lookup('file', 'my-playbook.yml')
         | playbook_to_job_template(
             playbook='my-playbook.yml',
             project='my-project',
             inventory='My Inventory') }}
"""

import re
import yaml


def _get_survey_type(value):
    """Map a Python value to an AAP survey field type."""
    if isinstance(value, bool):
        return 'multiplechoice'
    if isinstance(value, int):
        return 'integer'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, list):
        return 'multiselect' if len(value) < 10 else 'textarea'
    return 'text'


def _extract_variables(content, play):
    """Extract variables with preceding comments from raw playbook text."""
    vars_dict = play.get('vars') or {}
    if not vars_dict:
        return []

    lines = content.split('\n')
    variables = []

    for var_name, var_value in vars_dict.items():
        comment = None
        for i, line in enumerate(lines):
            if re.search(rf'^\s*{re.escape(var_name)}\s*:', line):
                # Check the line above for a comment
                if i > 0:
                    prev = lines[i - 1].strip()
                    if prev.startswith('#'):
                        comment = prev.lstrip('#').strip()
                # Inline comment takes precedence
                if '#' in line:
                    inline = line.split('#', 1)[1].strip()
                    if inline:
                        comment = inline
                break

        var_type = _get_survey_type(var_value)
        question = {
            'question_name': comment or "Variable: %s" % var_name,
            'question_description': "Variable: %s" % var_name,
            'variable': var_name,
            'type': var_type,
            'required': False,
        }

        if var_type == 'multiplechoice':
            question['choices'] = ['true', 'false']
            question['default'] = str(var_value).lower()
        elif var_type == 'multiselect' and isinstance(var_value, list):
            question['choices'] = [str(x) for x in var_value]
            question['default'] = str(var_value[0]) if var_value else ''
        else:
            question['default'] = str(var_value)

        variables.append(question)

    return variables


def playbook_to_job_template(content, playbook, project='ai-hacking',
                              inventory='Demo Inventory'):
    """
    Filter: convert raw playbook YAML text into an AAP job template config.

    Args:
        content:   Raw playbook file contents (string).
        playbook:  Filename of the playbook (used in the template config).
        project:   AAP project name.
        inventory: AAP inventory name.

    Returns:
        dict with a single 'job_templates' list entry ready for
        ansible.controller.job_template.
    """
    parsed = yaml.safe_load(content)
    if not parsed or not isinstance(parsed, list) or len(parsed) == 0:
        raise ValueError("Playbook must contain at least one play")

    play = parsed[0]
    template = {
        'name': play.get('name', 'Unnamed Playbook'),
        'job_type': 'run',
        'inventory': inventory,
        'project': project,
        'playbook': playbook,
        'ask_variables_on_launch': True,
    }

    survey_spec = _extract_variables(content, play)
    if survey_spec:
        template['survey_enabled'] = True
        template['survey'] = {
            'name': '',
            'description': '',
            'spec': survey_spec,
        }

    return template


class FilterModule:
    """Ansible filter plugin registration."""

    def filters(self):
        return {
            'playbook_to_job_template': playbook_to_job_template,
        }
