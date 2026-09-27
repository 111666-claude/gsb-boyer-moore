import io
import random
import unittest
from contextlib import redirect_stdout

from bmsearch.cli import main
from bmsearch.search import SearchError, build_shift_table, search


def naive_search(text, pattern):
    """朴素逐位扫描，作为对照口径。"""
    size = len(pattern)
    return [i for i in range(len(text) - size + 1) if text[i:i + size] == pattern]


class TableTest(unittest.TestCase):
    def test_last_char_excluded(self):
        table = build_shift_table("abac")
        self.assertEqual(table["a"], 2)
        self.assertEqual(table["b"], 1)
        self.assertNotIn("c", table)

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

    def test_overlapping_matches(self):
        positions, _ = search("aaaaa", "aa")
        self.assertEqual(positions, [0, 1, 2, 3])

    def test_missed_match_after_mismatch(self):
        positions, _ = search("abaa", "aa")
        self.assertEqual(positions, [2])

    def test_comparisons_within_text_length(self):
        text = "e" * 400 + "abcde"
        positions, comparisons = search(text, "abcde")
        self.assertEqual(positions, [400])
        self.assertLessEqual(comparisons, len(text))

    def test_deterministic(self):
        first = search("abaaabaaaa", "aa")
        second = search("abaaabaaaa", "aa")
        self.assertEqual(first, second)


class NaiveCrossCheckTest(unittest.TestCase):
    def test_random_against_naive(self):
        rng = random.Random(20260928)
        alphabet = "abcde"
        diffs = 0
        for _ in range(2000):
            text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 60)))
            pattern = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 6)))
            positions, _ = search(text, pattern)
            if positions != naive_search(text, pattern):
                diffs += 1
        self.assertEqual(diffs, 0)

    def test_large_text_single_pass(self):
        text = "abcde" * 2_000_000  # 10 MB
        pattern = "x" * 63 + "y"
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

    def test_missing_arguments(self):
        self.assertEqual(main(["--text", "abc"]), 2)


if __name__ == "__main__":
    unittest.main()
