from enum import Enum


class TemplateType(str, Enum):
    """Enum defining supported template types."""

    STRING = "string"
    JINJA2 = "jinja2"
