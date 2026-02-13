# Examples

## Mixed Variable Types

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
    # Enable automatic backups
    enable_backups: true
    # List of databases to create
    databases:
      - app_db
      - test_db
```

```bash
ansible-navigator run scripts/aap-deploy-config.yml --mode stdout \
  -e playbook_file=database-setup.yml \
  -e aap_inventory="Database Servers"
```

Generated survey fields:
- **db_engine** (text) - default: "postgresql"
- **db_version** (integer) - default: 14
- **enable_backups** (multiplechoice) - choices: true/false, default: true
- **databases** (multiselect) - choices: app_db, test_db

## Custom Project and Inventory

```bash
ansible-navigator run scripts/aap-deploy-config.yml --mode stdout \
  -e playbook_file=apache-webserver-role.yml \
  -e aap_project="my-other-project" \
  -e aap_inventory="Production Web Servers"
```

## Updating an Existing Template

Modify the playbook, push, then redeploy. The `ansible.controller` module handles create-or-update idempotently:

```bash
git add apache-webserver-role.yml && git commit -m "Add max_connections variable" && git push
ansible-navigator run scripts/aap-deploy-config.yml --mode stdout \
  -e playbook_file=apache-webserver-role.yml
```

## Using the Filter in a Custom Playbook

The `playbook_to_job_template` filter can be used directly:

```yaml
- name: Generate config for review
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Parse playbook into job template config
      ansible.builtin.set_fact:
        template: >-
          {{ lookup('file', 'apache-webserver-role.yml')
             | playbook_to_job_template(
                 playbook='apache-webserver-role.yml',
                 project='ai-hacking',
                 inventory='Demo Inventory') }}

    - name: Show the generated config
      ansible.builtin.debug:
        msg: "{{ template | to_nice_yaml }}"
```
