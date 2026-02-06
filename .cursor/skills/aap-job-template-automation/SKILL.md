---
name: aap-job-template-automation
description: Automates AAP job template creation after playbook changes are pushed to remote. Syncs projects and creates job templates with surveys from playbook variables. Use when a new playbook is added to the repository and has been pushed to the remote git repository, or when the user mentions AAP automation, job template creation, or AAP config as code.
---

# AAP Job Template Automation

This skill automates the creation of Ansible Automation Platform (AAP) job templates when new playbooks are added to the repository.

## Activation Trigger

**IMPORTANT**: This skill should only be activated AFTER:
1. A new playbook file (`.yml` or `.yaml`) has been added or modified
2. The changes have been committed to git
3. The changes have been pushed to the remote repository

Verify the push status before proceeding:
```bash
git status
```

## Required Environment Variables

The following environment variables must be set for AAP config as code:

```bash
export AAP_HOSTNAME=https://aap.example.com
export AAP_USERNAME=admin
export AAP_PASSWORD=<password>

# Alternatively, use a token instead of password:
# export AAP_TOKEN=<token>
```

These variables are automatically passed through to the execution environment via `ansible-navigator.yml` configuration.

## Workflow

### Step 1: Verify Prerequisites

Before starting, verify:
- [ ] Playbook changes are committed
- [ ] Changes are pushed to remote repository
- [ ] Required environment variables are set (AAP_HOSTNAME, AAP_USERNAME, AAP_PASSWORD or AAP_TOKEN)

Check environment variables:
```bash
echo "AAP_HOSTNAME: ${AAP_HOSTNAME:-NOT SET}"
echo "AAP_USERNAME: ${AAP_USERNAME:-NOT SET}"
echo "AAP_PASSWORD: ${AAP_PASSWORD:+SET}"
echo "AAP_TOKEN: ${AAP_TOKEN:+SET}"
```

### Step 2: Sync Project to AAP

Use the project sync playbook to sync the current project to AAP:

```bash
ansible-navigator run scripts/aap-sync-project.yml
```

This ensures AAP has the latest version of all playbooks, including the newly added one.

### Step 3: Create Job Template

Run the job template creation script:

```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py <playbook-file>
```

This script will:
1. Parse the playbook to extract the `name:` field
2. Identify all variables defined in the `vars:` section
3. Create a job template in AAP using the playbook name
4. Generate a survey with fields for all playbook variables
5. Enable the survey automatically

### Step 4: Verify Creation

Check that the job template was created successfully:

```bash
ansible-navigator run scripts/aap-list-job-templates.yml
```

Or verify directly in the AAP UI at: `${AAP_HOSTNAME}/#/templates/job_template`

## Playbook Variable Detection

The skill extracts variables from the playbook's `vars:` section. For example:

```yaml
- name: My Playbook
  hosts: all
  vars:
    my_variable: "default value"
    another_var: 123
```

Results in survey fields:
- `my_variable` (text field, default: "default value")
- `another_var` (integer field, default: 123)

### Survey Field Types

Variables are mapped to survey field types based on their values:
- String values → Text field
- Integer/float values → Integer/Float field  
- Boolean values → Multiple choice (true/false)
- List values → Multiple choice (if short) or Textarea (if long)

### Variable Comments as Labels

Comments above variables are used as survey field labels:

```yaml
vars:
  # The welcome message shown on the page
  welcome_message: "Hello World"
```

Results in a survey field with label: "The welcome message shown on the page"

## Example Usage

```bash
# After adding apache-webserver-role.yml and pushing to remote
cd /home/matt/projects/github/l3acon/ai-hacking

# 1. Verify push status
git status  # Should show "Your branch is up to date"

# 2. Sync project to AAP
ansible-navigator run scripts/aap-sync-project.yml

# 3. Create job template
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py apache-webserver-role.yml

# 4. Verify in AAP
ansible-navigator run scripts/aap-list-job-templates.yml
```

## Troubleshooting

### Project Sync Fails

If project sync fails, verify:
- AAP credentials are correct
- Project exists in AAP
- Git repository URL is accessible from AAP

### Job Template Creation Fails

Common issues:
- **Template already exists**: Delete the old template or use `--update` flag
- **Invalid playbook path**: Ensure the playbook file exists and path is correct
- **Missing inventory**: Specify inventory with `--inventory` flag
- **Permission denied**: Verify AAP user has template creation permissions

### Survey Not Created

If no survey is created:
- Verify the playbook has a `vars:` section
- Check that variables are properly formatted in YAML
- Review script output for parsing errors

## Additional Resources

- For AAP API details, see [AAP_API_REFERENCE.md](AAP_API_REFERENCE.md)
- For script customization, see [scripts/README.md](scripts/README.md)
