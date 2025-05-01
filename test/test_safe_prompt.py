import pytest
from pydantic import BaseModel

from safe_prompt.prompt_validation import TemplateType
from safe_prompt.safe_prompt import SafePrompt


# Using a name that doesn't start with "Test" to avoid pytest collection warnings
class UserModel(BaseModel):
    name: str
    age: int
    city: str = "Default City"


class TestSafePrompt:
    def test_init_with_valid_string_template(self):
        template = "Hello {name}, you are {age} years old and live in {city}."
        safe_prompt = SafePrompt(template, UserModel)
        assert safe_prompt.template == template
        assert safe_prompt.model_class == UserModel
        assert safe_prompt.template_type == TemplateType.STRING

    def test_init_with_valid_jinja2_template(self):
        template = (
            "Hello {{ name }}, you are {{ age }} years old and live in {{ city }}."
        )
        safe_prompt = SafePrompt(template, UserModel, template_type=TemplateType.JINJA2)
        assert safe_prompt.template == template
        assert safe_prompt.model_class == UserModel
        assert safe_prompt.template_type == TemplateType.JINJA2

    def test_init_with_invalid_template_raises_error(self):
        template = "Hello {name}, you are {age} years old and your email is {email}."
        with pytest.raises(ValueError) as excinfo:
            SafePrompt(template, UserModel)
        assert "Template references missing fields in model" in str(excinfo.value)

    def test_init_with_runtime_validation_disabled(self):
        template = "Hello {name}, you are {age} years old and your email is {email}."
        # This should not raise an error because runtime validation is disabled
        safe_prompt = SafePrompt(template, UserModel, runtime_validation=False)
        assert safe_prompt.template == template

    def test_validate_template_method(self):
        template = "Hello {name}, you are {age} years old and live in {city}."
        safe_prompt = SafePrompt(template, UserModel, runtime_validation=False)
        # Manually validate the template
        safe_prompt.validate_template()
        # No exception should be raised

    def test_validate_template_method_with_invalid_template(self):
        template = "Hello {name}, you are {age} years old and your email is {email}."
        safe_prompt = SafePrompt(template, UserModel, runtime_validation=False)
        # Manually validate the template
        with pytest.raises(ValueError) as excinfo:
            safe_prompt.validate_template()
        assert "Template references missing fields in model" in str(excinfo.value)

    def test_render_string_template(self):
        template = "Hello {name}, you are {age} years old and live in {city}."
        safe_prompt = SafePrompt(template, UserModel)
        model_instance = UserModel(name="John", age=30, city="New York")
        rendered = safe_prompt.render(model_instance)
        assert rendered == "Hello John, you are 30 years old and live in New York."

    def test_render_jinja2_template(self):
        template = (
            "Hello {{ name }}, you are {{ age }} years old and live in {{ city }}."
        )
        safe_prompt = SafePrompt(template, UserModel, template_type=TemplateType.JINJA2)
        model_instance = UserModel(name="John", age=30, city="New York")
        rendered = safe_prompt.render(model_instance)
        assert rendered == "Hello John, you are 30 years old and live in New York."

    def test_render_jinja2_template_with_control_structures(self):
        template = """
        Hello {{ name }},
        {% if age > 18 %}
        You are an adult.
        {% else %}
        You are a minor.
        {% endif %}
        You live in {{ city }}.
        """
        safe_prompt = SafePrompt(template, UserModel, template_type=TemplateType.JINJA2)

        # Test with adult
        adult = UserModel(name="John", age=30, city="New York")
        rendered_adult = safe_prompt.render(adult)
        assert "Hello John," in rendered_adult
        assert "You are an adult." in rendered_adult
        assert "You live in New York." in rendered_adult

        # Test with minor
        minor = UserModel(name="Jane", age=16, city="Boston")
        rendered_minor = safe_prompt.render(minor)
        assert "Hello Jane," in rendered_minor
        assert "You are a minor." in rendered_minor
        assert "You live in Boston." in rendered_minor

    def test_render_with_default_values(self):
        template = "Hello {name}, you are {age} years old and live in {city}."
        safe_prompt = SafePrompt(template, UserModel)
        model_instance = UserModel(name="John", age=30)  # city will use default value
        rendered = safe_prompt.render(model_instance)
        assert rendered == "Hello John, you are 30 years old and live in Default City."

    def test_render_with_unsupported_template_type(self):
        template = "Hello {name}"
        # Create SafePrompt with runtime_validation=False to bypass initial validation
        safe_prompt = SafePrompt(template, UserModel, runtime_validation=False)
        # Set an unsupported template type
        safe_prompt.template_type = "unsupported_type"

        model_instance = UserModel(name="John", age=30)
        with pytest.raises(ValueError) as excinfo:
            safe_prompt.render(model_instance)
        assert "Unsupported template type" in str(excinfo.value)
