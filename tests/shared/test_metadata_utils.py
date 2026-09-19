"""SDK-defined: `get_display_name` in `mcp.shared.metadata_utils`, direct unit tests.

Its signature covers `Tool | Resource | Prompt | ResourceTemplate | Implementation`;
`Implementation` (`clientInfo`/`serverInfo`) had no coverage anywhere before this file.
"""

from collections.abc import Callable

import pytest
from mcp_types import Implementation, Prompt, Resource, ResourceTemplate, Tool, ToolAnnotations

from mcp.shared.metadata_utils import get_display_name

_NonToolTarget = Resource | Prompt | ResourceTemplate | Implementation


def _make_resource(name: str, title: str | None) -> Resource:
    return Resource(uri="file:///x", name=name, title=title)


def _make_prompt(name: str, title: str | None) -> Prompt:
    return Prompt(name=name, title=title)


def _make_resource_template(name: str, title: str | None) -> ResourceTemplate:
    return ResourceTemplate(uri_template="file:///{id}", name=name, title=title)


def _make_implementation(name: str, title: str | None) -> Implementation:
    return Implementation(name=name, version="1.0", title=title)


_NON_TOOL_FACTORIES: list[Callable[[str, str | None], _NonToolTarget]] = [
    _make_resource,
    _make_prompt,
    _make_resource_template,
    _make_implementation,
]
_NON_TOOL_IDS = ["Resource", "Prompt", "ResourceTemplate", "Implementation"]


def test_tool_uses_name_when_no_title_or_annotations_title() -> None:
    """SDK-defined: Tool falls back to `name` when neither `title` nor `annotations.title` is set."""
    tool = Tool(name="my_tool", input_schema={})
    assert get_display_name(tool) == "my_tool"


def test_tool_prefers_annotations_title_over_name() -> None:
    """SDK-defined: Tool's `annotations.title` wins over `name` when `title` is unset."""
    tool = Tool(name="my_tool", input_schema={}, annotations=ToolAnnotations(title="Friendly Name"))
    assert get_display_name(tool) == "Friendly Name"


def test_tool_prefers_title_over_annotations_title_and_name() -> None:
    """SDK-defined: Tool's `title` wins over both `annotations.title` and `name`."""
    tool = Tool(
        name="my_tool",
        input_schema={},
        title="Top-Level Title",
        annotations=ToolAnnotations(title="Friendly Name"),
    )
    assert get_display_name(tool) == "Top-Level Title"


def test_tool_with_annotations_but_no_annotations_title_falls_back_to_name() -> None:
    """SDK-defined: `annotations` set but its own `title` unset falls through to `name`, not `AttributeError`."""
    tool = Tool(name="my_tool", input_schema={}, annotations=ToolAnnotations())
    assert get_display_name(tool) == "my_tool"


def test_tool_with_empty_string_title_returns_empty_string() -> None:
    """Pinned gap: `title=""` is falsy but not `None`, so it's returned as-is rather than treated as unset."""
    tool = Tool(name="my_tool", input_schema={}, title="")
    assert get_display_name(tool) == ""


# Implementation is new here: it shares Resource/Prompt/ResourceTemplate's title>name precedence
# but had no test anywhere before this file, despite being part of get_display_name's signature.
@pytest.mark.parametrize("make_obj", _NON_TOOL_FACTORIES, ids=_NON_TOOL_IDS)
def test_non_tool_types_use_name_when_title_is_unset(make_obj: Callable[[str, str | None], _NonToolTarget]) -> None:
    """SDK-defined: non-Tool types fall back to `name` when `title` is unset."""
    obj = make_obj("my_object", None)
    assert get_display_name(obj) == "my_object"


@pytest.mark.parametrize("make_obj", _NON_TOOL_FACTORIES, ids=_NON_TOOL_IDS)
def test_non_tool_types_prefer_title_over_name(make_obj: Callable[[str, str | None], _NonToolTarget]) -> None:
    """SDK-defined: non-Tool types prefer `title` over `name` when both are set."""
    obj = make_obj("my_object", "Friendly Name")
    assert get_display_name(obj) == "Friendly Name"


@pytest.mark.parametrize("make_obj", _NON_TOOL_FACTORIES, ids=_NON_TOOL_IDS)
def test_non_tool_types_with_empty_string_title_return_empty_string(
    make_obj: Callable[[str, str | None], _NonToolTarget],
) -> None:
    """Pinned gap: same as Tool — `title=""` is returned as-is, not treated as unset."""
    obj = make_obj("my_object", "")
    assert get_display_name(obj) == ""
