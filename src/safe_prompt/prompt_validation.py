from typing import Type

from pydantic import BaseModel

from safe_prompt.interface_types import TemplateType
from safe_prompt.placeholder_extraction import (
    extract_placeholders,
)


def validate_template(
    template: str, template_type: TemplateType, model_class: Type[BaseModel]
) -> None:
    """
    Validate that a template only references fields that exist in the model class.

    Args:
        template: The template string to validate
        template_type: The type of template (string or jinja2)
        model_class: The Pydantic model class to validate against

    Raises:
        ValueError: If the template references fields not present in the model
    """
    placeholders = extract_placeholders(template, template_type)
    model_fields = set(model_class.model_fields.keys())
    missing = placeholders - model_fields
    if missing:
        raise ValueError(f"Template references missing fields in model: {missing}")
