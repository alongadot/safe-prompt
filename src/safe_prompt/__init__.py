"""
Safe Prompt: A type-safe, Pydantic-powered library for defining and validating prompts in LLM workflows.
"""

from importlib.metadata import PackageNotFoundError, version

from safe_prompt.prompt_validation import TemplateType
from safe_prompt.safe_prompt import SafePrompt

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # fallback for development install
    __version__ = "0.0.0"

__all__ = ["SafePrompt", "TemplateType"]
