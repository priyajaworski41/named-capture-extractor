"""Named Capture Extractor: run a regex, return named groups as a dict."""

from .core import extract, extract_first, InvalidPatternError

__all__ = ["extract", "extract_first", "InvalidPatternError"]
