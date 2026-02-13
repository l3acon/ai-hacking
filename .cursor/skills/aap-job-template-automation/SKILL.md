---
name: aap-job-template-automation
description: Automates AAP job template creation after playbook changes are pushed to remote. Syncs projects and creates job templates with surveys from playbook variables. Use when a new playbook is added to the repository and has been pushed to the remote git repository, or when the user mentions AAP automation, job template creation, or AAP config as code.
---

# AAP Job Template Automation

Automates creating AAP job templates when new playbooks are added. A filter plugin (`playbook_to_job_template`) parses the playbook and generates Config as Code, then the `ansible.controller` collection deploys to AAP.

## Prerequisites

- Playbook changes committed and pushed to the remote repository
- Environment variables set (passed through to the EE via `ansible-navigator.yml`):
  ```bash
  export AAP_HOSTNAME=https://aap.example.com
  export AAP_USERNAME=admin
  export AAP_PASSWORD=<password>
  # OR: export AAP_TOKEN=<token>
  ```
- `ansible.cfg` at project root with `filter_plugins = ./filter_plugins`
- All `ansible-navigator` commands require `--mode stdout`

## Workflow

### Step 1: Ensure the AAP project exists

If this is the first time, create the project in AAP. This only needs to run once per AAP instance:

```bash
ansible-navigator run scripts/aap-create-project.yml --mode stdout
```

The project is configured with `scm_update_on_launch: true`, so it syncs automatically when job templates run. To sync manually:

```bash
ansible-navigator run scripts/aap-sync-project.yml --mode stdout
```

### Step 2: Deploy the job template

```bash
ansible-navigator run scripts/aap-deploy-config.yml --mode stdout \
  -e playbook_file=<playbook-filename>
```

This playbook reads the playbook file, passes it through the `playbook_to_job_template` filter to generate a job template config with auto-generated survey, then deploys via `ansible.controller.job_template`.

Optional overrides:
- `-e aap_project=<name>` (default: `ai-hacking`)
- `-e aap_inventory=<name>` (default: `Demo Inventory`)

### Step 3: Verify (optional)

```bash
ansible-navigator run scripts/aap-list-job-templates.yml --mode stdout
```

## Helper Playbooks

| Playbook | Purpose |
|----------|---------|
| `scripts/aap-create-project.yml` | Create the AAP project (one-time setup) |
| `scripts/aap-sync-project.yml` | Sync the project from git |
| `scripts/aap-deploy-config.yml` | Generate + deploy a job template |
| `scripts/aap-list-projects.yml` | List projects in AAP |
| `scripts/aap-list-job-templates.yml` | List job templates in AAP |

## Survey Generation

The filter plugin (`filter_plugins/aap_config.py`) extracts variables from the playbook's `vars:` section:
- Comments above variables become question labels
- Types are inferred: `str` -> text, `int` -> integer, `bool` -> multiplechoice, `list` -> multiselect

```yaml
vars:
  # The welcome message shown on the page
  welcome_message: "Hello World"
```

Becomes a survey field: question_name "The welcome message shown on the page", type text, default "Hello World".

## Notes

- AAP_HOSTNAME trailing slashes are stripped automatically in all playbooks
- The `ansible.controller.export` module does not work on AAP 2.5+; list playbooks use `uri` with `api/controller/v2/` instead
- The deploy playbook resolves the playbook file relative to the project root (`playbook_dir + '/../'`)
- The `ansible.controller` modules handle API version compatibility across AAP 2.4/2.5/2.6

## Additional Resources

- For more examples, see [EXAMPLES.md](EXAMPLES.md)
