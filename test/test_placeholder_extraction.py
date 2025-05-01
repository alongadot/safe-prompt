from safe_prompt.placeholder_extraction import (
    extract_placeholders_from_string,
    extract_placeholders_from_jinja2,
)


class TestExtractPlaceholders:
    def test_extract_placeholders_from_string(self):
        template = "Hello {name}, you are {age} years old and live in {city}."
        placeholders = extract_placeholders_from_string(template)
        assert placeholders == {"name", "age", "city"}

    def test_extract_placeholders_from_string_with_no_placeholders(self):
        template = "Hello, this is a static text."
        placeholders = extract_placeholders_from_string(template)
        assert placeholders == set()

    def test_extract_placeholders_from_string_with_duplicate_placeholders(self):
        template = "Hello {name}, your name is {name}."
        placeholders = extract_placeholders_from_string(template)
        assert placeholders == {"name"}

    def test_extract_placeholders_from_jinja2(self):
        template = (
            "Hello {{ name }}, you are {{ age }} years old and live in {{ city }}."
        )
        placeholders = extract_placeholders_from_jinja2(template)
        assert placeholders == {"name", "age", "city"}

    def test_extract_placeholders_from_jinja2_with_no_placeholders(self):
        template = "Hello, this is a static text."
        placeholders = extract_placeholders_from_jinja2(template)
        assert placeholders == set()

    def test_extract_placeholders_from_jinja2_with_control_structures(self):
        template = """
        Hello {{ name }},
        {% if age > 18 %}
            You are an adult.
        {% else %}
            You are a minor.
        {% endif %}
        You live in {{ city }}.
        """
        placeholders = extract_placeholders_from_jinja2(template)
        assert placeholders == {"name", "age", "city"}
