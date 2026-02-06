# AAP Job Template Automation Scripts

This directory contains helper scripts for the AAP job template automation skill.

## Scripts

### create_job_template.py

Python script that creates AAP job templates with automatic survey generation.

**Requirements:**
```bash
pip install pyyaml requests
```

**Usage:**
```bash
python3 create_job_template.py <playbook-file> [options]
```

**Options:**
- `--project NAME` - AAP project name (default: ai-hacking)
- `--inventory NAME` - AAP inventory name (uses first available if not specified)
- `--update` - Update existing template if it already exists

**Environment Variables:**
- `AAP_HOSTNAME` - AAP server URL (required)
- `AAP_USERNAME` - AAP username (required if not using token)
- `AAP_PASSWORD` - AAP password (required if not using token)
- `AAP_TOKEN` - AAP OAuth token (alternative to username/password)

**Examples:**
```bash
# Create job template for apache-webserver-role.yml
python3 create_job_template.py apache-webserver-role.yml

# Specify custom inventory
python3 create_job_template.py apache-webserver-role.yml --inventory "Production Servers"

# Update existing template
python3 create_job_template.py apache-webserver-role.yml --update
```

### Survey Generation

The script automatically generates surveys from playbook variables:

1. **Variable Detection**: Parses the `vars:` section of the playbook
2. **Type Inference**: Determines appropriate survey field type based on value
3. **Comment Extraction**: Uses comments as field labels/descriptions
4. **Default Values**: Pre-fills survey with playbook default values

**Variable Type Mapping:**
- `str` → Text field
- `int` → Integer field
- `float` → Float field
- `bool` → Multiple choice (true/false)
- `list` (< 10 items) → Multi-select
- `list` (≥ 10 items) → Textarea

## Customization

### Custom Survey Field Types

To override automatic type detection, you can modify the `_get_variable_type()` method in `create_job_template.py`:

```python
@staticmethod
def _get_variable_type(value: Any) -> str:
    # Add custom logic here
    if isinstance(value, str) and len(value) > 100:
        return 'textarea'  # Use textarea for long strings
    # ... existing logic
```

### Custom Variable Filtering

To exclude certain variables from surveys, modify `_extract_variables_with_comments()`:

```python
# Skip internal variables
if var_name.startswith('_') or var_name.startswith('ansible_'):
    continue
```

### Custom Project Name

Change the default project name in the argument parser:

```python
parser.add_argument(
    '--project',
    default='your-project-name',  # Change this
    help='AAP project name'
)
```

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL certificate errors with self-signed certificates:

```python
# In AAPClient.__init__()
self.session.verify = False  # Disable SSL verification (not recommended)
```

Or set the environment variable:
```bash
export PYTHONHTTPSVERIFY=0
```

### Authentication Issues

Test your AAP credentials:
```bash
curl -k -u $AAP_USERNAME:$AAP_PASSWORD $AAP_HOSTNAME/api/v2/ping/
```

Or with token:
```bash
curl -k -H "Authorization: Bearer $AAP_TOKEN" $AAP_HOSTNAME/api/v2/ping/
```

### Playbook Parsing Errors

If the script fails to parse your playbook:
1. Verify YAML syntax: `yamllint playbook.yml`
2. Ensure the playbook has a `name:` field in the first play
3. Check that `vars:` section is properly formatted

## Dependencies

The script requires:
- Python 3.6+
- `pyyaml` - YAML parsing
- `requests` - HTTP client for AAP API

Install with:
```bash
pip install pyyaml requests
```

Or add to `requirements.txt`:
```
pyyaml>=6.0
requests>=2.28.0
```
