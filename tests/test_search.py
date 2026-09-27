import io
import random
import unittest
from contextlib import redirect_stdout

from bmsearch.cli import main
from bmsearch.search import SearchError, build_shift_table, search


def naive_search(text, pattern):
    """朴素逐位扫描，作为对照口径。"""
    return [index for index in range(len(text) - len(pattern) + 1)
            if text[index:index + len(pattern)] == pattern]


class TableTest(unittest.TestCase):
    def test_last_occurrence_before_final_char_wins(self):
        table = build_shift_table("abac")
        self.assertEqual(table["a"], 2)
        self.assertEqual(table["b"], 1)

    def test_final_char_not_in_table(self):
        table = build_shift_table("abac")
        self.assertNotIn("c", table)
        self.assertEqual(build_shift_table("aa"), {"a": 0})

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
        positions, comparisons = search("ab", "abcdef")
        self.assertEqual(positions, [])

    def test_match_at_the_end(self):
        positions, _ = search("aab", "ab")
        self.assertEqual(positions, [1])

    def test_overlapping_matches(self):
        positions, _ = search("aaaaa", "aa")
        self.assertEqual(positions, [0, 1, 2, 3])

    def test_overlap_with_self_overlap_pattern(self):
        positions, _ = search("ababab", "abab")
        self.assertEqual(positions, [0, 2])

    def test_previously_missed_match(self):
        positions, _ = search("abaa", "aa")
        self.assertEqual(positions, [2])

    def test_empty_pattern_raises(self):
        with self.assertRaises(SearchError):
            search("abc", "")

    def test_positions_are_sorted(self):
        positions, _ = search("abcabcabc", "abc")
        self.assertEqual(positions, sorted(positions))

    def test_comparisons_within_text_length(self):
        text = "e" * 400 + "abcde"
        positions, comparisons = search(text, "abcde")
        self.assertEqual(positions, [400])
        self.assertLessEqual(comparisons, len(text))

    def test_deterministic(self):
        first = search("abcabcabc", "abc")
        second = search("abcabcabc", "abc")
        self.assertEqual(first, second)


class RandomizedCrossCheckTest(unittest.TestCase):
    def test_matches_naive_scan(self):
        rng = random.Random(20260927)
        alphabet = "abcde"
        for _ in range(2000):
            text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 60)))
            pattern = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 8)))
            positions, _ = search(text, pattern)
            self.assertEqual(positions, naive_search(text, pattern),
                             msg="text=%r pattern=%r" % (text, pattern))


class LargeInputTest(unittest.TestCase):
    def test_ten_megabytes_single_pass(self):
        pattern = "cd" * 32
        text = "ab" * (5 * 1024 * 1024)
        positions, comparisons = search(text, pattern)
        self.assertEqual(positions, [])
        self.assertLessEqual(comparisons, len(text))


class CliTest(unittest.TestCase):
    def test_prints_matches(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--text", "hello world", "--pattern", "world"])
        self.assertEqual(code, 0)
        lines = buffer.getvalue().split()
        self.assertEqual(lines[0], "matches=6")
        self.assertTrue(lines[1].startswith("comparisons="))

    def test_prints_empty_matches(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--text", "hello", "--pattern", "xyz"])
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue().split()[0], "matches=")

    def test_empty_pattern_reports_error(self):
        self.assertEqual(main(["--text", "abc", "--pattern", ""]), 1)

    def test_missing_arguments(self):
        self.assertEqual(main(["--text", "abc"]), 2)


if __name__ == "__main__":
    unittest.main()
