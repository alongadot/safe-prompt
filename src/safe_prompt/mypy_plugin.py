"""
Mypy plugin for safe_prompt: statically validate that SafePrompt templates
only reference fields present on the given Pydantic model class.
"""

from typing import Set
import sys
from mypy.plugin import Plugin, FunctionContext
from mypy.types import Instance, Type as MypyType, TypeType, CallableType
from mypy.nodes import StrExpr, MemberExpr, Var

from safe_prompt.placeholder_extraction import (
    extract_placeholders,
)
from safe_prompt.prompt_validation import TemplateType


def safe_prompt_init_hook(ctx: FunctionContext) -> MypyType:
    # 1) Grab the literal template
    if not ctx.args or not ctx.args[0]:
        return ctx.default_return_type
    tpl_expr = ctx.args[0][0]
    if not isinstance(tpl_expr, StrExpr):
        return ctx.default_return_type
    template_str = tpl_expr.value

    # 2) Figure out which template type was passed
    print("🔤 figuring out template type", file=sys.stderr)
    tpl_type = TemplateType.STRING
    if len(ctx.args) > 2 and ctx.args[2]:
        kind = ctx.args[2][0]
        if isinstance(kind, MemberExpr) and kind.name == "JINJA2":
            tpl_type = TemplateType.JINJA2

    # 3) Extract placeholders
    placeholders: Set[str] = extract_placeholders(template_str, tpl_type)

    if len(ctx.arg_types) < 2 or not ctx.arg_types[1]:
        return ctx.default_return_type
    model_arg = ctx.arg_types[1][0]

    if isinstance(model_arg, TypeType):
        inst = model_arg.item
        if not isinstance(inst, Instance):
            return ctx.default_return_type
        model_info = inst.type

    elif isinstance(model_arg, CallableType):
        ret = model_arg.ret_type
        if not isinstance(ret, Instance):
            return ctx.default_return_type
        model_info = ret.type

    else:
        ctx.api.fail(
            "Second argument to SafePrompt must be a BaseModel class", tpl_expr
        )
        return ctx.default_return_type

    # 5) Gather its declared fields
    fields = {
        name
        for name, symnode in model_info.names.items()
        if isinstance(symnode.node, Var)
    }

    # 6) Compare and fail if anything is missing
    missing = placeholders - fields
    if missing:
        ctx.api.fail(
            f"SafePrompt template refers to missing fields on '{model_info.name}': {sorted(missing)}",
            tpl_expr,
        )
    return ctx.default_return_type


class SafePromptPlugin(Plugin):
    def get_function_hook(self, fullname: str):
        if fullname in (
            "safe_prompt.safe_prompt.SafePrompt",
            "safe_prompt.SafePrompt",
        ):
            return safe_prompt_init_hook
        return None


def plugin(version: str):
    """Entry point for mypy to discover this plugin."""
    return SafePromptPlugin
