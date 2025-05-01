# Safe Prompt

[![PyPI version](https://badge.fury.io/py/safe-prompt.svg)](https://badge.fury.io/py/safe-prompt)
[![Python Versions](https://img.shields.io/pypi/pyversions/safe-prompt.svg)](https://pypi.org/project/safe-prompt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A type-safe, Pydantic-powered library for defining and validating prompts in LLM workflows.

## Overview

Safe Prompt provides an opinionated way to define prompts in LLM workflows with compile-time and runtime validation. It leverages Pydantic models to ensure that templates only reference fields that exist in your data models, preventing runtime errors when rendering templates with missing fields.

Key features:
- **Type safety**: Catch template errors at compile time with mypy plugin
- **Runtime validation**: Validate templates against Pydantic models
- **Multiple template engines**: Support for Python string formatting and Jinja2 templates
- **Flexible rendering**: Render templates with Pydantic model instances

## Installation

```bash
pip install safe-prompt
```

To enable the mypy plugin for compile-time validation, add the following to your `pyproject.toml`:

```toml
[tool.mypy]
plugins = ["safe_prompt.mypy_plugin"]
```

## Usage

### Basic Example

```python
from pydantic import BaseModel
from safe_prompt import SafePrompt, TemplateType

# Define your data model with Pydantic
class UserProfile(BaseModel):
    name: str
    age: int
    occupation: str
    years_experience: int = 0

# Create a template with Python string formatting
template = """
Hello {name}!

I see you're {age} years old and work as a {occupation}.
"""

# Create a SafePrompt instance
prompt = SafePrompt(template, UserProfile)

# Create a model instance
user = UserProfile(
    name="Alice",
    age=28,
    occupation="Software Engineer",
    years_experience=5
)

# Render the template
rendered_prompt = prompt.render(user)
print(rendered_prompt)
```

### Using Jinja2 Templates

```python
from safe_prompt import SafePrompt, TemplateType

# Create a template with Jinja2 syntax
jinja_template = """
Hello {{ name }}!

{% if age > 30 %}
You have significant experience as a {{ occupation }}.
{% else %}
You're early in your career as a {{ occupation }}.
{% endif %}

{% if years_experience > 0 %}
With {{ years_experience }} years of experience, you must have learned a lot.
{% endif %}
"""

# Create a SafePrompt instance with Jinja2 template type
prompt = SafePrompt(jinja_template, UserProfile, template_type=TemplateType.JINJA2)

# Render the template with the same model instance
rendered_prompt = prompt.render(user)
print(rendered_prompt)
```

### Compile-time Validation with mypy

Safe Prompt includes a mypy plugin that validates templates at compile time:

```python
# This will be caught by mypy if the plugin is enabled
invalid_template = "Hello {name}, your email is {email}!"  # 'email' is not in UserProfile
prompt = SafePrompt(invalid_template, UserProfile)  # mypy error: SafePrompt template refers to missing fields on 'UserProfile': ['email']
```

### Runtime Validation

By default, SafePrompt validates templates at initialization time:

```python
try:
    # This will raise a ValueError at runtime
    prompt = SafePrompt("Hello {name}, your email is {email}!", UserProfile)
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: Validation error: Template references missing fields in model: {'email'}
```

You can disable runtime validation if needed:

```python
# No validation at initialization time
prompt = SafePrompt("Hello {name}!", UserProfile, runtime_validation=False)

# Manually validate later if needed
try:
    prompt.validate_template()
except ValueError as e:
    print(f"Validation error: {e}")
```

## Advanced Features

### Default Values

Safe Prompt works seamlessly with Pydantic's default values:

```python
class Message(BaseModel):
    recipient: str
    subject: str = "No Subject"
    body: str

template = "To: {recipient}\nSubject: {subject}\n\n{body}"
prompt = SafePrompt(template, Message)

# The 'subject' field will use its default value
message = Message(recipient="user@example.com", body="Hello there!")
print(prompt.render(message))
```

## Development

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/safe-prompt.git
   cd safe-prompt
   ```

2. Install development dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=safe_prompt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests to make sure everything works (`pytest`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure your code passes all tests and follows the project's coding style.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
