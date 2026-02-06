# AAP API Reference

Quick reference for Ansible Automation Platform (AAP) API v2 endpoints used in this skill.

## Authentication

### Token Authentication (Recommended)
```bash
curl -H "Authorization: Bearer $AAP_TOKEN" $AAP_HOSTNAME/api/v2/
```

### Basic Authentication
```bash
curl -u $AAP_USERNAME:$AAP_PASSWORD $AAP_HOSTNAME/api/v2/
```

## Common Endpoints

### Projects

**List Projects:**
```bash
GET /api/v2/projects/
```

**Update Project:**
```bash
POST /api/v2/projects/{id}/update/
```

**Get Project by Name:**
```bash
GET /api/v2/projects/?name=project-name
```

### Inventories

**List Inventories:**
```bash
GET /api/v2/inventories/
```

**Get Inventory by Name:**
```bash
GET /api/v2/inventories/?name=inventory-name
```

### Job Templates

**Create Job Template:**
```bash
POST /api/v2/job_templates/
{
  "name": "Template Name",
  "job_type": "run",
  "inventory": 1,
  "project": 2,
  "playbook": "playbook.yml",
  "ask_variables_on_launch": true
}
```

**Update Job Template:**
```bash
PATCH /api/v2/job_templates/{id}/
{
  "description": "Updated description"
}
```

**List Job Templates:**
```bash
GET /api/v2/job_templates/
```

### Surveys

**Create Survey:**
```bash
POST /api/v2/job_templates/{id}/survey_spec/
{
  "name": "Survey Name",
  "description": "Survey Description",
  "spec": [
    {
      "question_name": "Variable Label",
      "question_description": "Variable Description",
      "variable": "variable_name",
      "type": "text",
      "required": false,
      "default": "default_value"
    }
  ]
}
```

**Enable Survey:**
```bash
PATCH /api/v2/job_templates/{id}/
{
  "survey_enabled": true
}
```

### Survey Field Types

- `text` - Single-line text input
- `textarea` - Multi-line text input
- `password` - Password field (hidden input)
- `integer` - Integer number
- `float` - Floating point number
- `multiplechoice` - Radio buttons
- `multiselect` - Checkboxes

### Launch Job

**Launch Job Template:**
```bash
POST /api/v2/job_templates/{id}/launch/
{
  "extra_vars": {
    "variable_name": "value"
  }
}
```

## Using ansible.controller Collection

The AAP skill uses the `ansible.controller` collection for config as code:

### Project Update
```yaml
- name: Update project
  ansible.controller.project_update:
    project: "project-name"
    wait: true
    controller_host: "{{ aap_hostname }}"
    controller_username: "{{ aap_username }}"
    controller_password: "{{ aap_password }}"
```

### Job Template Creation
```yaml
- name: Create job template
  ansible.controller.job_template:
    name: "Template Name"
    job_type: run
    inventory: "Inventory Name"
    project: "Project Name"
    playbook: "playbook.yml"
    ask_variables_on_launch: true
    survey_enabled: true
    survey_spec: "{{ survey_spec }}"
    controller_host: "{{ aap_hostname }}"
    controller_username: "{{ aap_username }}"
    controller_password: "{{ aap_password }}"
```

## References

- [AAP API Documentation](https://docs.ansible.com/automation-controller/latest/html/controllerapi/index.html)
- [ansible.controller Collection](https://console.redhat.com/ansible/automation-hub/repo/published/ansible/controller)
