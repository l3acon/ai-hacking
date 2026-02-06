# AAP Job Template Automation - Examples

This document provides detailed examples of using the AAP job template automation skill.

## Example 1: Basic Playbook with Simple Variables

### Playbook: web-server-deploy.yml
```yaml
---
- name: Deploy Web Server
  hosts: webservers
  become: true
  vars:
    # The port number for the web server
    web_port: 80
    # Enable SSL/TLS encryption
    enable_ssl: false
    # Server administrator email
    admin_email: "admin@example.com"
  
  tasks:
    - name: Install web server
      ansible.builtin.package:
        name: httpd
        state: present
```

### Running the Automation

```bash
# 1. Commit and push the playbook
git add web-server-deploy.yml
git commit -m "Add web server deployment playbook"
git push origin main

# 2. Sync project to AAP
ansible-navigator run scripts/aap-sync-project.yml

# 3. Create job template with survey
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py web-server-deploy.yml
```

### Expected Survey Fields

The script will create a survey with these fields:
- **web_port** (integer): "The port number for the web server" (default: 80)
- **enable_ssl** (multiple choice): "Enable SSL/TLS encryption" (choices: true/false, default: false)
- **admin_email** (text): "Server administrator email" (default: "admin@example.com")

## Example 2: Complex Playbook with Nested Variables

### Playbook: database-setup.yml
```yaml
---
- name: Setup Database Server
  hosts: databases
  become: true
  vars:
    # Database engine to install
    db_engine: "postgresql"
    # Database version
    db_version: 14
    # Maximum number of connections
    max_connections: 100
    # Enable automatic backups
    enable_backups: true
    # Backup retention days
    backup_retention_days: 7
    # List of databases to create
    databases:
      - app_db
      - test_db
  
  tasks:
    - name: Install database
      ansible.builtin.package:
        name: "{{ db_engine }}"
        state: present
```

### Automation Process

```bash
# After committing and pushing
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  database-setup.yml \
  --inventory "Database Servers"
```

### Survey Output

Generated survey will include:
- **db_engine** (text): "Database engine to install"
- **db_version** (integer): "Database version"
- **max_connections** (integer): "Maximum number of connections"
- **enable_backups** (multiple choice): "Enable automatic backups"
- **backup_retention_days** (integer): "Backup retention days"
- **databases** (multiselect): "List of databases to create"

## Example 3: Using the Role-Based Playbook

### Our apache-webserver-role.yml

```yaml
---
- name: Setup Apache Web Server on RHEL using Role
  hosts: all
  become: true
  vars:
    # Set to true to use the server's IP address instead of FQDN
    use_ip_address: false
    # Customize the welcome message displayed on the web page
    welcome_message: "Apache Web Server is Running!"
  
  roles:
    - apache_webserver
```

### Automation Workflow

```bash
# 1. Verify the playbook is committed and pushed
git status  # Should show "Your branch is up to date with 'origin/main'"

# 2. Sync AAP project
ansible-navigator run scripts/aap-sync-project.yml

# 3. Create job template
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  apache-webserver-role.yml \
  --project ai-hacking

# 4. Verify creation
ansible-navigator run scripts/aap-list-job-templates.yml
```

### Survey Result

Creates a survey with:
- **use_ip_address** (multiple choice): "Set to true to use the server's IP address instead of FQDN" (choices: true/false, default: false)
- **welcome_message** (text): "Customize the welcome message displayed on the web page" (default: "Apache Web Server is Running!")

### Launching the Job in AAP

1. Navigate to AAP: `$AAP_HOSTNAME/#/templates`
2. Find "Setup Apache Web Server on RHEL using Role"
3. Click the rocket icon to launch
4. Fill in the survey:
   - **use_ip_address**: false
   - **welcome_message**: "Welcome to Production!"
5. Click "Launch"

## Example 4: Updating an Existing Template

If you modify the playbook and want to update the job template:

```bash
# Edit the playbook
vim apache-webserver-role.yml

# Add a new variable
# vars:
#   # Maximum number of concurrent connections
#   max_connections: 150

# Commit and push
git add apache-webserver-role.yml
git commit -m "Add max_connections variable"
git push origin main

# Sync project
ansible-navigator run scripts/aap-sync-project.yml

# Update the job template (--update flag)
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  apache-webserver-role.yml \
  --update
```

The survey will be recreated with all variables, including the new `max_connections` field.

## Example 5: Specifying Custom Inventory

```bash
# Use a specific inventory for production servers
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  apache-webserver-role.yml \
  --inventory "Production Web Servers"

# Or for development
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py \
  apache-webserver-role.yml \
  --inventory "Dev Environment"
```

## Troubleshooting Examples

### Example: Missing AAP Credentials

**Problem:**
```bash
$ python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py playbook.yml
Error: AAP_HOSTNAME environment variable is required
```

**Solution:**
```bash
# Set required environment variables
export AAP_HOSTNAME=https://aap.example.com
export AAP_USERNAME=admin
export AAP_PASSWORD=secret

# Or use a token
export AAP_TOKEN=your-oauth-token

# Try again
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py playbook.yml
```

### Example: Project Not Synced

**Problem:**
```bash
$ python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py new-playbook.yml
Error: Playbook 'new-playbook.yml' not found in project 'ai-hacking'
```

**Solution:**
```bash
# 1. Verify the playbook is committed and pushed
git status
git push origin main

# 2. Sync the project
ansible-navigator run scripts/aap-sync-project.yml

# 3. Try again
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py new-playbook.yml
```

### Example: Playbook Has No Variables

**Problem:**
Your playbook doesn't have any variables in the `vars:` section.

**Solution:**
The script will still create the job template, but without a survey:

```bash
$ python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py simple-playbook.yml
Parsing playbook: simple-playbook.yml
✓ Playbook name: Simple Playbook
✓ Found 0 variables
Creating job template 'Simple Playbook'...
✓ Job template created successfully (ID: 42)
```

To add a survey later, modify the playbook to include variables and run with `--update`:

```yaml
vars:
  # Some configuration option
  config_option: "value"
```

```bash
python3 .cursor/skills/aap-job-template-automation/scripts/create_job_template.py simple-playbook.yml --update
```
