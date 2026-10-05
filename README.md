Named Capture Extractor runs a Python regular expression against text and returns each match's named capture groups as a dictionary.

```python
from named_capture_extractor import extract, extract_first

# find every key=value pair in a string
for groups in extract(r"(?P<key>\w+)=(?P<val>\w+)", "a=1 b=2"):
    print(groups)  # {'key': 'a', 'val': '1'} then {'key': 'b', 'val': '2'}

# grab just the first match
first = extract_first(r"(?P<year>\d{4})", "founded 2001")
# first == {'year': '2001'}
```

## Why this exists

`re.match` returns a match object whose group values you access by index or by name. There's no built-in one-liner to turn a match into a plain `{name: value}` dict, which is the shape most callers actually want — for logging, JSON serialization, or passing to other functions. This library is that one-liner, with a couple of conveniences (accepting pre-compiled patterns, returning `None` for non-participating groups so you can tell "matched empty" from "did not match").

The trade-off: the library is strict. A pattern with zero named groups raises `InvalidPatternError`, because silently returning an empty dict would hide what is almost always a typo. If you want unnamed groups, use `re` directly.

## Awkward edge

When a named group lives inside one branch of an alternation and that branch doesn't match, `re` reports the group as `None` (not `""`). The dict you get back preserves that distinction: `None` means "did not participate", `""` means "matched but captured nothing". Plan your consumers accordingly.
