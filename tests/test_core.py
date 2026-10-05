import re
import unittest

from named_capture_extractor import extract, extract_first, InvalidPatternError


class TestExtract(unittest.TestCase):
    def test_single_match_returns_one_dict(self):
        pattern = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
        text = "2024-01-30"
        result = extract(pattern, text)
        self.assertEqual(result, [{"year": "2024", "month": "01", "day": "30"}])

    def test_multiple_matches_each_as_dict(self):
        pattern = r"(?P<key>\w+)=(?P<val>\w+)"
        text = "a=1 b=22 c=333"
        result = extract(pattern, text)
        self.assertEqual(result, [
            {"key": "a", "val": "1"},
            {"key": "b", "val": "22"},
            {"key": "c", "val": "333"},
        ])

    def test_no_matches_returns_empty_list(self):
        pattern = r"(?P<x>\d+)"
        result = extract(pattern, "no digits here")
        self.assertEqual(result, [])

    def test_non_participating_group_is_none(self):
        # When an alternation branch doesn't match, the groups in the other
        # branch don't participate; re returns None for them, not "".
        pattern = r"(?:(?P<a>foo)|(?P<b>bar))"
        result = extract(pattern, "bar")
        self.assertEqual(result, [{"a": None, "b": "bar"}])

    def test_empty_string_match_value_is_empty_string(self):
        # A group that matches but captures nothing is "", distinct from None.
        pattern = r"(?P<word>\w+)(?P<suffix>!?)"
        result = extract(pattern, "hi")
        self.assertEqual(result, [{"word": "hi", "suffix": ""}])

    def test_pattern_without_named_groups_raises(self):
        with self.assertRaises(InvalidPatternError):
            extract(r"\d+", "123")

    def test_empty_pattern_string_raises(self):
        with self.assertRaises(InvalidPatternError):
            extract("", "text")

    def test_malformed_pattern_raises(self):
        with self.assertRaises(InvalidPatternError):
            extract(r"(?P<name", "text")

    def test_accepts_precompiled_pattern(self):
        compiled = re.compile(r"(?P<x>\d+)")
        result = extract(compiled, "42")
        self.assertEqual(result, [{"x": "42"}])

    def test_duplicate_name_across_branches_raises(self):
        # re does not permit the same group name in multiple branches of an
        # alternation; it raises re.error on compile. The library surfaces
        # that as InvalidPatternError.
        with self.assertRaises(InvalidPatternError):
            extract(r"(?:(?P<val>foo)|(?P<val>bar))", "bar")

    def test_non_string_text_raises(self):
        with self.assertRaises(TypeError):
            extract(r"(?P<x>\d+)", 123)

    def test_non_string_non_pattern_pattern_raises(self):
        with self.assertRaises(InvalidPatternError):
            extract(123, "text")


class TestExtractFirst(unittest.TestCase):
    def test_returns_first_match(self):
        pattern = r"(?P<n>\d+)"
        result = extract_first(pattern, "a 1 b 2 c 3")
        self.assertEqual(result, {"n": "1"})

    def test_returns_none_when_no_match(self):
        pattern = r"(?P<n>\d+)"
        result = extract_first(pattern, "no digits")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
