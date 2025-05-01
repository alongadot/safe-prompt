import pytest
from pydantic import BaseModel

from safe_prompt.prompt_validation import TemplateType, validate_template


# Using a name that doesn't start with "Test" to avoid pytest collection warnings
class UserModel(BaseModel):
    name: str
    age: int
    city: str = "Default City"


class TestValidateTemplate:
    def test_validate_template_string_valid(self):
        template = "Hello {name}, you are {age} years old and live in {city}."
        validate_template(template, TemplateType.STRING, UserModel)
        # No exception should be raised

    def test_validate_template_jinja2_valid(self):
        template = "Hello {{ name }}, you are {{ age }} years old and live in {{ city }}."
        validate_template(template, TemplateType.JINJA2, UserModel)
        # No exception should be raised

    def test_validate_template_string_invalid(self):
        template = "Hello {name}, you are {age} years old and your email is {email}."
        with pytest.raises(ValueError) as excinfo:
            validate_template(template, TemplateType.STRING, UserModel)
        assert "Template references missing fields in model" in str(excinfo.value)
        assert "email" in str(excinfo.value)

    def test_validate_template_jinja2_invalid(self):
        template = "Hello {{ name }}, you are {{ age }} years old and your email is {{ email }}."
        with pytest.raises(ValueError) as excinfo:
            validate_template(template, TemplateType.JINJA2, UserModel)
        assert "Template references missing fields in model" in str(excinfo.value)
        assert "email" in str(excinfo.value)

    def test_validate_template_unsupported_type(self):
        template = "Hello {name}"
        with pytest.raises(ValueError) as excinfo:
            validate_template(template, "unsupported_type", UserModel)
        assert "Unsupported template type" in str(excinfo.value)
