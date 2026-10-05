import re
import sys
from typing import Dict, List, Optional, Union, Pattern


class InvalidPatternError(ValueError):
    """
    Raised when the supplied pattern is not syntactically a valid Python
    regular expression, OR when it compiles but contains zero named capture
    groups. We treat namelessness as a usage error for this library because
    the whole point is to return named captures; silently returning an empty
    dict would mask a typo'd pattern.
    """


def _compile(pattern: Union[str, Pattern[str]]) -> Pattern[str]:
    """
    Accept a raw string or an already-compiled Pattern. Returning a compiled
    Pattern lets callers reuse a pre-compiled regex across calls without us
    recompiling each time, which matters for tight loops.
    """
    if isinstance(pattern, Pattern):
        return pattern
    if isinstance(pattern, str):
        try:
            return re.compile(pattern)
        except re.error as exc:
            raise InvalidPatternError(
                f"Invalid regular expression: {pattern!r}: {exc}"
            ) from exc
    raise InvalidPatternError(
        f"Pattern must be str or compiled re.Pattern, got {type(pattern).__name__}"
    )


def _named_groups(pattern: Pattern[str]) -> List[str]:
    """
    Extract the declared named groups from the compiled pattern. We use
    groupindex (a dict of name -> index) rather than scanning the pattern
    text ourselves; relying on the engine's own accounting is safer than
    reimplementing parsing of inline (?P<...>) syntax including alternation
    and nested groups.
    """
    return list(pattern.groupindex.keys())


def _slice_match(match: re.Match, names: List[str]) -> Dict[str, str]:
    """
    Build the result dict for one match object. A named group that did not
    participate (e.g. in an unused alternation branch) is None under Python's
    re module; we map that to None in the dict rather than "" so the caller
    can distinguish "matched empty string" from "did not match".
    """
    out: Dict[str, str] = {}
    for name in names:
        out[name] = match.group(name)
    return out


def extract(
    pattern: Union[str, Pattern[str]],
    text: str,
) -> List[Dict[str, Optional[str]]]:
    """
    Run `pattern` against `text` and return a list of dicts, one per match,
    each mapping every named group to its value (or None if that group did
    not participate in the match).

    Returns an empty list if there are no matches. Raises
    InvalidPatternError if the pattern is malformed or has no named groups.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"text must be str, got {type(text).__name__}"
        )
    compiled = _compile(pattern)
    names = _named_groups(compiled)
    if not names:
        raise InvalidPatternError(
            "Pattern must contain at least one named capture group "
            "((?P<name>...)). None found."
        )
    return [_slice_match(m, names) for m in compiled.finditer(text)]


def extract_first(
    pattern: Union[str, Pattern[str]],
    text: str,
) -> Optional[Dict[str, Optional[str]]]:
    """
    Convenience wrapper: return the first match's group dict, or None if the
    pattern doesn't match at all. This is the common case for parsing a single
    value out of a line; extract() exists for find-all use.
    """
    results = extract(pattern, text)
    if not results:
        return None
    return results[0]
