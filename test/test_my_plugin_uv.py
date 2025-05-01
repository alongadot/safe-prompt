# tests/test_mypy_plugin_uv.py
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

PROJECT_ROOT = Path(__file__).parent.parent  # adjust if needed


def run_mypy(target: Path) -> subprocess.CompletedProcess:
    """
    Run `uv run mypy` on the given target file, using our project root
    so that pyproject.toml & plugin are discovered.
    """
    cmd = ["uv", "run", "mypy", "--show-traceback", str(target)]
    return subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def write_test_file(tmp_path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


def test_failing_template(write_test_file):
    code = dedent("""
    from pydantic import BaseModel
    from safe_prompt import SafePrompt, TemplateType

    class User(BaseModel):
        name: str
        age: int

    # missing 'email' ⇒ should error
    SafePrompt("Hello {name}, e-mail: {email}", User, TemplateType.STRING)
    """)
    test_file = write_test_file("fail.py", code)
    result = run_mypy(test_file)

    # mypy exit code is non-zero on errors
    assert result.returncode != 0, result.stdout + result.stderr
    # and our plugin's message appears
    assert "missing fields on 'User': ['email']" in result.stdout
    print(result.stdout)


def test_passing_template(write_test_file):
    code = dedent("""
    from pydantic import BaseModel
    from safe_prompt import SafePrompt, TemplateType

    class User(BaseModel):
        name: str
        age: int

    # all placeholders exist ⇒ no error
    SafePrompt("Hello {name}, age: {age}", User, TemplateType.STRING)
    """)
    test_file = write_test_file("pass.py", code)
    result = run_mypy(test_file)

    # no errors ⇒ exit code 0
    assert result.returncode == 0, result.stdout + result.stderr
