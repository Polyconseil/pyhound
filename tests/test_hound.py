import re
from unittest import TestCase

from pyhound import hound


class TestGetLinesWithContext(TestCase):
    """Test ``get_lines_with_context()``."""

    def test_no_context(self):
        res = list(
            hound.get_lines_with_context(
                "The match", 1,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"])
        )
        self.assertEqual(
            res,
            [(1, hound.LINE_KIND_MATCH, "The match")]
        )

    def test_before_context(self):
        res = list(
            hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_before=3)
        )
        self.assertEqual(
            res,
            [(1, hound.LINE_KIND_CONTEXT, "Line 1"),
             (2, hound.LINE_KIND_CONTEXT, "Line 2"),
             (3, hound.LINE_KIND_MATCH, "The match")]
        )

    def test_after_context(self):
        res = list(hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_after=3)
        )
        self.assertEqual(
            res,
            [(3, hound.LINE_KIND_MATCH, "The match"),
             (4, hound.LINE_KIND_CONTEXT, "Line 4"),
             (5, hound.LINE_KIND_CONTEXT, "Line 5")]
        )

    def test_before_and_after_context(self):
        res = list(
            hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_before=3,
                requested_after=3)
        )
        self.assertEqual(
            res,
            [(1, hound.LINE_KIND_CONTEXT, "Line 1"),
             (2, hound.LINE_KIND_CONTEXT, "Line 2"),
             (3, hound.LINE_KIND_MATCH, "The match"),
             (4, hound.LINE_KIND_CONTEXT, "Line 4"),
             (5, hound.LINE_KIND_CONTEXT, "Line 5")]
        )

    def test_context_basics(self):
        res = list(
            hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_context=5)
        )
        self.assertEqual(
            res,
            [(1, hound.LINE_KIND_CONTEXT, "Line 1"),
             (2, hound.LINE_KIND_CONTEXT, "Line 2"),
             (3, hound.LINE_KIND_MATCH, "The match"),
             (4, hound.LINE_KIND_CONTEXT, "Line 4"),
             (5, hound.LINE_KIND_CONTEXT, "Line 5")]
        )

    def test_context_request_less_than_available(self):
        # Ask for a context of 3 while we have 2 before and 2 after.
        res = list(
            hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_context=3)
        )
        self.assertEqual(
            res,
            [(2, hound.LINE_KIND_CONTEXT, "Line 2"),
             (3, hound.LINE_KIND_MATCH, "The match"),
             (4, hound.LINE_KIND_CONTEXT, "Line 4")]
        )

    def test_context_request_less_than_available_prefer_before(self):
        # Ask for a context of 4 while we have 2 before and 2
        # after. We prefer showing 2 "before lines" and 1 "after
        # line", instead of 1 "before line" and 2 "after lines".
        res = list(
            hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_context=4)
        )
        self.assertEqual(
            res,
            [(1, hound.LINE_KIND_CONTEXT, "Line 1"),
             (2, hound.LINE_KIND_CONTEXT, "Line 2"),
             (3, hound.LINE_KIND_MATCH, "The match"),
             (4, hound.LINE_KIND_CONTEXT, "Line 4")]
        )

    def test_context_request_more_than_available(self):
        # Ask for a context of 10 while we have only 2 before and 2
        # after.
        res = list(
            hound.get_lines_with_context(
                "The match", 3,
                lines_before=["Line 1", "Line 2"],
                lines_after=["Line 4", "Line 5"],
                requested_context=10)
        )
        self.assertEqual(
            res,
            [(1, hound.LINE_KIND_CONTEXT, "Line 1"),
             (2, hound.LINE_KIND_CONTEXT, "Line 2"),
             (3, hound.LINE_KIND_MATCH, "The match"),
             (4, hound.LINE_KIND_CONTEXT, "Line 4"),
             (5, hound.LINE_KIND_CONTEXT, "Line 5")]
        )


class TestMergeLines(TestCase):
    """Test ``merge_lines()``."""

    def test_basics(self):
        # The first two values of each line item are dummy ones. They
        # are not used by the implementation.
        lines = [
            ('', '', 1, hound.LINE_KIND_CONTEXT, "Line 1"),
            ('', '', 2, hound.LINE_KIND_CONTEXT, "Line 2"),
            ('', '', 3, hound.LINE_KIND_MATCH, "The first match"),
        ]
        lines.extend([
            ('', '', 2, hound.LINE_KIND_CONTEXT, "Line 2"),
            ('', '', 3, hound.LINE_KIND_CONTEXT, "The first match"),
            ('', '', 4, hound.LINE_KIND_MATCH, "The second match"),
        ])
        merged = list(hound.merge_lines(lines))
        self.assertEqual(
            merged,
            [('', '', 1, hound.LINE_KIND_CONTEXT, "Line 1"),
             ('', '', 2, hound.LINE_KIND_CONTEXT, "Line 2"),
             ('', '', 3, hound.LINE_KIND_MATCH, "The first match"),
             ('', '', 4, hound.LINE_KIND_MATCH, "The second match")]
        )


class TestColorizeMatch(TestCase):
    """Test ``colorize_match()``."""

    def test_pattern_appears_once(self):
        line = "The revolution will be colorized."
        pattern = re.compile("revolution")
        colorized = hound.colorize_match(line, pattern, '[%s]')
        self.assertEqual(colorized, "The [revolution] will be colorized.")

    def test_pattern_appears_many_times(self):
        line = "Some spam in your spammy spam."
        pattern = re.compile("spam")
        colorized = hound.colorize_match(line, pattern, '[%s]')
        self.assertEqual(colorized, "Some [spam] in your [spam]my [spam].")

    def test_pattern_case(self):
        line = "I am John. John!"
        pattern = re.compile("john")
        colorized = hound.colorize_match(line, pattern, '[%s]')
        self.assertEqual(colorized, "I am John. John!")
        pattern = re.compile("john", re.IGNORECASE)
        colorized = hound.colorize_match(line, pattern, '[%s]')
        self.assertEqual(colorized, "I am [John]. [John]!")

    def test_pattern_with_non_ascii(self):
        line = "I am Jón."
        pattern = re.compile("jón")
        colorized = hound.colorize_match(line, pattern, '[%s]')
        self.assertEqual(colorized, "I am Jón.")
        pattern = re.compile("jón", re.IGNORECASE)
        colorized = hound.colorize_match(line, pattern, '[%s]')
        self.assertEqual(colorized, "I am [Jón].")
