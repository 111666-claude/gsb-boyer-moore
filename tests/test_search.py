import io
import unittest
from contextlib import redirect_stdout

from bmsearch.cli import main
from bmsearch.search import SearchError, build_shift_table, search


class TableTest(unittest.TestCase):
    def test_last_occurrence_wins(self):
        table = build_shift_table("abac")
        self.assertEqual(table["a"], 2)
        self.assertEqual(table["b"], 1)
        self.assertEqual(table["c"], 3)

    def test_empty_pattern(self):
        self.assertEqual(build_shift_table(""), {})


class SearchTest(unittest.TestCase):
    def test_single_match(self):
        positions, comparisons = search("hello world", "world")
        self.assertEqual(positions, [6])
        self.assertGreater(comparisons, 0)

    def test_no_match(self):
        positions, _ = search("hello", "xyz")
        self.assertEqual(positions, [])

    def test_pattern_longer_than_text(self):
        positions, _ = search("ab", "abcdef")
        self.assertEqual(positions, [])

    def test_match_at_the_end(self):
        positions, _ = search("aab", "ab")
        self.assertEqual(positions, [1])

    def test_empty_pattern_raises(self):
        with self.assertRaises(SearchError):
            search("abc", "")

    def test_positions_are_sorted(self):
        positions, _ = search("abcabcabc", "abc")
        self.assertEqual(positions, sorted(positions))


class CliTest(unittest.TestCase):
    def test_prints_matches(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--text", "hello world", "--pattern", "world"])
        self.assertEqual(code, 0)
        lines = buffer.getvalue().split()
        self.assertEqual(lines[0], "matches=6")
        self.assertTrue(lines[1].startswith("comparisons="))

    def test_missing_arguments(self):
        self.assertEqual(main(["--text", "abc"]), 2)


if __name__ == "__main__":
    unittest.main()
