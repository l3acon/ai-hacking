# Quick Setup Guide

Follow these steps to set up and use the AAP Job Template Automation skill for the first time.

## Step 1: Set Environment Variables

Add these to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# AAP Credentials
export AAP_HOSTNAME=https://aap.example.com
export AAP_USERNAME=admin
export AAP_PASSWORD=your-password

# OR use a token instead:
# export AAP_TOKEN=your-oauth-token
```

Reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

Verify:
```bash
echo $AAP_HOSTNAME
```

## Step 2: Install Python Dependencies

```bash
pip install -r .cursor/skills/aap-job-template-automation/requirements.txt
```

This installs:
- `pyyaml` - For parsing playbook YAML
- `requests` - For AAP API calls

## Step 3: Verify AAP Connectivity

Test your credentials:

```bash
# If using username/password
curl -k -u $AAP_USERNAME:$AAP_PASSWORD $AAP_HOSTNAME/api/v2/ping/

# If using token
curl -k -H "Authorization: Bearer $AAP_TOKEN" $AAP_HOSTNAME/api/v2/ping/
```

You should see a JSON response with `"ha": false` or similar.

## Step 4: Verify ansible-navigator Configuration

Check that the AAP credentials are passed through:

```bash
cat ansible-navigator.yml
```

Ensure these lines exist:
```yaml
environment-variables:
  pass:
    - AAP_HOSTNAME
    - AAP_USERNAME
    - AAP_PASSWORD
    - AAP_TOKEN
```

## Step 5: Test the Workflow

### A. Test Project Sync

```bash
ansible-navigator run scripts/aap-sync-project.yml
```

Expected output:
```
========================================
Project Sync Complete
========================================
Project: ai-hacking
Status: success
...
```

### B. Test Job Template Creation

Use the existing `apache-webserver-role.yml` as a test:

```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  apache-webserver-role.yml
```

Expected output:
```
Parsing playbook: apache-webserver-role.yml
✓ Playbook name: Setup Apache Web Server on RHEL using Role
✓ Found 2 variables
Creating job template 'Setup Apache Web Server on RHEL using Role'...
✓ Job template created successfully (ID: XX)
Creating survey with 2 variables...
✓ Survey created and enabled

============================================================
SUCCESS!
...
```

### C. Verify in AAP

```bash
ansible-navigator run scripts/aap-list-job-templates.yml
```

Or visit AAP web UI:
```
$AAP_HOSTNAME/#/templates/job_template
```

## Common Setup Issues

### Issue: "command not found: pip"

Install pip:
```bash
# On RHEL/Fedora
sudo dnf install python3-pip

# On Ubuntu/Debian
sudo apt install python3-pip
```

### Issue: "Permission denied" when installing packages

Use `--user` flag:
```bash
pip install --user -r .cursor/skills/aap-job-template-automation/requirements.txt
```

### Issue: SSL certificate errors

If using self-signed certificates, temporarily disable verification:
```bash
export PYTHONHTTPSVERIFY=0
```

**Note:** This is not recommended for production.

### Issue: "Project 'ai-hacking' not found"

The project name in AAP must match. Change the default:
```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  playbook.yml \
  --project "your-actual-project-name"
```

## Next Steps

Once setup is complete:

1. **Read the skill documentation:** `.cursor/skills/aap-job-template-automation/SKILL.md`
2. **Review examples:** `.cursor/skills/aap-job-template-automation/EXAMPLES.md`
3. **Try with your own playbooks:** Create a new playbook, commit, push, and run the automation

## Getting Help

- Check [EXAMPLES.md](EXAMPLES.md) for detailed usage examples
- Check [scripts/README.md](scripts/README.md) for script customization
- Check [AAP_API_REFERENCE.md](AAP_API_REFERENCE.md) for API details

## Skill Activation

The agent will automatically activate this skill when:
- A new playbook is added to the repository (after git push)
- You mention "AAP automation" or "job template creation"
- You ask about AAP config as code

Just tell the agent: "I've added a new playbook, let's set it up in AAP" and the skill will guide the automation.
