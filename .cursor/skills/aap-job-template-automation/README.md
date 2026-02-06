# AAP Job Template Automation Skill

An agent skill that automates the creation of Ansible Automation Platform (AAP) job templates with automatic survey generation from playbook variables.

## Overview

This skill streamlines the workflow of deploying new playbooks to AAP by:
1. Syncing the project repository to AAP
2. Creating a job template from the playbook
3. Automatically generating surveys from playbook variables
4. Enabling the survey for runtime configuration

## Quick Start

### Prerequisites

1. **Environment Variables** - Set AAP credentials:
   ```bash
   export AAP_HOSTNAME=https://aap.example.com
   export AAP_USERNAME=admin
   export AAP_PASSWORD=<password>
   # OR use a token:
   # export AAP_TOKEN=<token>
   ```

2. **Python Dependencies** - Install required packages:
   ```bash
   pip install -r .cursor/skills/aap-job-template-automation/requirements.txt
   ```

3. **Git Status** - Ensure your playbook changes are committed and pushed:
   ```bash
   git status  # Should show "Your branch is up to date"
   ```

### Usage

```bash
# 1. Sync project to AAP
ansible-navigator run scripts/aap-sync-project.yml

# 2. Create job template with survey
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py <playbook-file>

# 3. Verify in AAP
ansible-navigator run scripts/aap-list-job-templates.yml
```

### Example

```bash
# Create job template for apache-webserver-role.yml
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py apache-webserver-role.yml
```

Output:
```
Parsing playbook: apache-webserver-role.yml
✓ Playbook name: Setup Apache Web Server on RHEL using Role
✓ Found 2 variables
Creating job template 'Setup Apache Web Server on RHEL using Role'...
✓ Job template created successfully (ID: 42)
Creating survey with 2 variables...
✓ Survey created and enabled

============================================================
SUCCESS!
============================================================
Job template 'Setup Apache Web Server on RHEL using Role' is ready to use
View in AAP: https://aap.example.com/#/templates/job_template/42
============================================================
```

## Features

### Automatic Survey Generation

The skill intelligently creates survey fields from playbook variables:

**Input (playbook):**
```yaml
vars:
  # The welcome message displayed on the page
  welcome_message: "Hello World"
  # Maximum connections allowed
  max_connections: 100
  # Enable debug mode
  debug_mode: false
```

**Output (AAP survey):**
- **welcome_message** (text): "The welcome message displayed on the page" → default: "Hello World"
- **max_connections** (integer): "Maximum connections allowed" → default: 100
- **debug_mode** (multiple choice): "Enable debug mode" → choices: [true, false], default: false

### Smart Type Detection

Variables are automatically mapped to appropriate survey field types:
- **String values** → Text field
- **Integer/float values** → Integer/Float field
- **Boolean values** → Multiple choice (true/false)
- **Short lists** → Multiple select
- **Long lists** → Textarea

### Comment Extraction

Comments above or inline with variables become survey field labels and descriptions.

## Directory Structure

```
.cursor/skills/aap-job-template-automation/
├── SKILL.md                    # Main skill instructions
├── EXAMPLES.md                 # Detailed usage examples
├── AAP_API_REFERENCE.md       # AAP API documentation
├── requirements.txt           # Python dependencies
├── scripts/
│   ├── create_job_template.py # Main automation script
│   └── README.md              # Script documentation
```

## Documentation

- **[SKILL.md](SKILL.md)** - Main skill instructions and workflow
- **[EXAMPLES.md](EXAMPLES.md)** - Detailed examples and troubleshooting
- **[AAP_API_REFERENCE.md](AAP_API_REFERENCE.md)** - AAP API reference
- **[scripts/README.md](scripts/README.md)** - Script documentation and customization

## Configuration

### Default Project Name

The script defaults to project name `ai-hacking`. Change it with:
```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  playbook.yml \
  --project "your-project-name"
```

### Default Inventory

If no inventory is specified, the script uses the first available inventory. Specify with:
```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  playbook.yml \
  --inventory "Production Servers"
```

### Updating Templates

To update an existing job template:
```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  playbook.yml \
  --update
```

## Troubleshooting

### Common Issues

1. **"AAP_HOSTNAME environment variable is required"**
   - Set AAP credentials: `export AAP_HOSTNAME=https://aap.example.com`

2. **"Project 'ai-hacking' not found in AAP"**
   - Verify project exists in AAP or specify correct project with `--project`

3. **"Playbook 'x.yml' not found in project"**
   - Ensure changes are pushed: `git push origin main`
   - Sync project: `ansible-navigator run scripts/aap-sync-project.yml`

4. **"No inventories found in AAP"**
   - Create an inventory in AAP or specify with `--inventory`

See [EXAMPLES.md](EXAMPLES.md) for more troubleshooting scenarios.

## Requirements

- Python 3.6+
- `pyyaml` >= 6.0
- `requests` >= 2.28.0
- ansible-navigator with AAP execution environment
- AAP credentials with permissions to create job templates

## License

Part of the ai-hacking project.
