from typing import TypeVar, Type, Generic

from jinja2 import Template
from pydantic import BaseModel

from safe_prompt.interface_types import TemplateType
from safe_prompt.prompt_validation import validate_template

ModelT = TypeVar("ModelT", bound=BaseModel)


class SafePrompt(Generic[ModelT]):
    """
    A class for safely rendering templates with validated Pydantic models.

    This class ensures that templates only reference fields that exist in the model,
    preventing runtime errors when rendering templates with missing fields.

    Attributes:
        model_class: The Pydantic model class to validate against
        template: The template string
        template_type: The type of template (string or jinja2)
    """

    def __init__(
        self,
        template: str,
        model_class: Type[ModelT],
        template_type: TemplateType = TemplateType.STRING,
        runtime_validation: bool = True,
    ):
        """
        Initialize a SafePrompt instance.

        Args:
            template: The template string
            model_class: The Pydantic model class to validate against
            template_type: The type of template (string or jinja2)
            runtime_validation: Whether to validate the template at initialization
        """
        self.model_class = model_class
        self.template = template
        self.template_type = template_type
        if runtime_validation:
            self.validate_template()

    def validate_template(self) -> None:
        """
        Validate that the template only references fields that exist in the model class.

        Raises:
            ValueError: If the template references fields not present in the model
        """
        validate_template(self.template, self.template_type, self.model_class)

    def render(self, instance: ModelT) -> str:
        """
        Render the template with the provided model instance.

        Args:
            instance: A Pydantic model instance to use for rendering

        Returns:
            The rendered template string

        Raises:
            ValueError: If the template type is not supported
        """
        if self.template_type == TemplateType.STRING:
            return self.template.format(**instance.model_dump())
        elif self.template_type == TemplateType.JINJA2:
            template = Template(self.template)
            return template.render(**instance.model_dump())
        else:
            raise ValueError(f"Unsupported template type: {self.template_type}")
