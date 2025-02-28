import functools
import inspect
import re
from typing import Callable, Iterable, Optional, Any

mention_reg = re.compile(r"@(everyone|here|[!&]?[0-9]{17,20})")


def escape_mentions(content: str) -> str:
    """
    Escape mentions that could ping someone in a string

    note:
        This does not escape channel mentions as they do not ping anybody

    Args:
        content: The string to escape

    Returns:
        Processed string
    """
    return mention_reg.sub("@\u200b\\1", content)


def find(predicate: Callable, sequence: Iterable) -> Optional[Any]:
    """
    Find the first element in a sequence that matches the predicate.

    ??? Hint "Example Usage:"
        ```python
        member = find(lambda m: m.name == "UserName", guild.members)
        ```
    Args:
        predicate: A callable that returns a boolean value
        sequence: A sequence to be searched

    Returns:
        A match if found, otherwise None
    """
    for el in sequence:
        if predicate(el):
            return el
    return None


def wrap_partial(obj, cls):
    """
    🎁 Wraps a commands callback objects into partials

    !!! note
        This is used internally, you shouldn't need to use this function

    Args:
        obj: The command object to process
        cls: The class to use in partials

    Returns:
        The original command object with its callback methods wrapped
    """
    obj.callback = functools.partial(obj.callback, cls)

    if hasattr(obj, "error_callback") and inspect.ismethod(obj.error_callback):
        obj.error_callback = functools.partial(obj.error_callback, cls)
    if hasattr(obj, "pre_run_callback") and inspect.ismethod(obj.pre_run_callback):
        obj.pre_run_callback = functools.partial(obj.pre_run_callback, cls)
    if hasattr(obj, "post_run_callback") and inspect.ismethod(obj.post_run_callback):
        obj.post_run_callback = functools.partial(obj.post_run_callback, cls)

    return obj
