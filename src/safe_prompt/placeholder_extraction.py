import string
from jinja2 import Environment, meta

from safe_prompt.interface_types import TemplateType


def extract_placeholders_from_string(template: str) -> set[str]:
    """
    Extract placeholders from a Python string format template.

    Args:
        template: A string template with Python format placeholders like "{field_name}"

    Returns:
        A set of field names found in the template
    """
    formatter = string.Formatter()
    return {
        field_name for _, field_name, _, _ in formatter.parse(template) if field_name
    }


def extract_placeholders_from_jinja2(template: str) -> set[str]:
    """
    Extract placeholders from a Jinja2 template.

    Args:
        template: A Jinja2 template with placeholders like "{{ field_name }}"

    Returns:
        A set of variable names found in the template
    """
    env = Environment()
    parsed_content = env.parse(template)
    return meta.find_undeclared_variables(parsed_content)


def extract_placeholders(template: str, template_type: TemplateType) -> set[str]:
    """
    Extract placeholders from a template string based on its type.

    Args:
        template: The template string to extract placeholders from
        template_type: The type of template (string or jinja2)

    Returns:
        A set of placeholders found in the template
    """
    if template_type == TemplateType.STRING:
        return extract_placeholders_from_string(template)
    elif template_type == TemplateType.JINJA2:
        return extract_placeholders_from_jinja2(template)
    else:
        raise ValueError(f"Unsupported template type: {template_type}")
