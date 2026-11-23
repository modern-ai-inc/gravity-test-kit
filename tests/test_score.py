import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path

import score

ROOT = Path(__file__).resolve().parents[1]
KEY = ["id", "question", "right_figure", "tolerance", "definition", "source"]
ANS = ["id", "question", "ai_figure", "ai", "asked_on", "full_answer"]


def write(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


class ParseTest(unittest.TestCase):
    def test_figures(self):
        p = score.parse_figure
        self.assertEqual(p("1,234"), Decimal(1234))
        self.assertEqual(p("$18,400.50"), Decimal("18400.50"))
        self.assertEqual(p("(12)"), Decimal(-12))
        self.assertEqual(p("-3"), Decimal(-3))
        self.assertEqual(p("38.5%"), p("0.385"))  # a percent is a fraction
        self.assertEqual(p("1.2m"), Decimal(1200000))
        self.assertEqual(p("Up"), "up")

    def test_not_a_single_figure(self):
        for t in ("", "about 12", "12 people", "1,23", "(5", "--5", "12-15", "1,190 2", "12 15"):
            self.assertIsNone(score.parse_figure(t), t)  # two figures are never merged into one


class CellTest(unittest.TestCase):
    def test_formula_text_is_kept_as_text(self):
        for text in ("=1+1", "+SUM(A1)", "@x", "-cmd"):
            self.assertEqual(score.cell(text), "'" + text)

    def test_figures_and_words_are_unchanged(self):
        for text in ("-5", "-$100", "(1,190)", "2.4%", "up", "", "How many orders?"):
            self.assertEqual(score.cell(text), text)


class ScoreTest(unittest.TestCase):
    def run_score(self, key_rows, ans_rows):
        with tempfile.TemporaryDirectory() as tmp:
            k, a = Path(tmp) / "k.csv", Path(tmp) / "a.csv"
            write(k, KEY, key_rows)
            write(a, ANS, ans_rows)
            with redirect_stdout(io.StringIO()) as out:
                code = score.main([str(k), str(a)])
            rows = list(csv.DictReader(open(Path(tmp) / "results.csv")))
        return code, out.getvalue(), {r["id"]: r["verdict"] for r in rows}

    def test_verdicts_and_counts(self):
        q = "How many orders in October 2026?"
        code, out, v = self.run_score(
            [["Q1", q, "1,190", "0", "", ""], ["Q2", q, "$100", "$5", "", ""], ["Q3", q, "2.4%", "0.1%", "", ""],
             ["Q4", q, "up", "0", "", ""], ["Q5", q, "7", "0", "", ""]],
            [["Q1", q, "1190", "", "", ""], ["Q2", q, "$106", "", "", ""], ["Q3", q, "2.45%", "", "", ""],
             ["Q4", q, "", "", "", ""], ["Q9", q, "1", "", "", ""]])
        self.assertEqual(code, 0)
        self.assertEqual(v, {"Q1": "right", "Q2": "wrong", "Q3": "right", "Q4": "no figure", "Q5": "not asked"})
        self.assertIn("Wrong:     1", out)
        self.assertIn("Ignored, not in the answer key: Q9", out)
        self.assertNotIn("%", out.split("Results")[0])  # counts, never percentages

    def test_a_different_currency_is_wrong(self):
        q = "Revenue in October 2026?"
        _, _, v = self.run_score([["Q1", q, "$100", "0", "", ""], ["Q2", q, "$100", "0", "", ""]],
                                 [["Q1", q, "€100", "", "", ""], ["Q2", q, "100", "", "", ""]])
        self.assertEqual(v, {"Q1": "wrong", "Q2": "right"})

    def test_never_overwrites_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            k, a = Path(tmp) / "k.csv", Path(tmp) / "a.csv"
            write(k, KEY, [["Q1", "x", "1", "0", "", ""]])
            write(a, ANS, [["Q1", "x", "2", "", "", ""]])
            (Path(tmp) / "results.csv").write_text("my causes\n")
            with redirect_stdout(io.StringIO()):
                score.main([str(k), str(a)])
            self.assertEqual((Path(tmp) / "results.csv").read_text(), "my causes\n")
            self.assertTrue((Path(tmp) / "results-2.csv").exists())

    def test_question_words_must_match(self):
        with self.assertRaises(SystemExit):
            self.run_score([["Q1", "How many orders?", "5", "0", "", ""]], [["Q1", "How many sales?", "5", "", "", ""]])

    def test_missing_right_figure_and_duplicates_stop(self):
        with self.assertRaises(SystemExit):
            self.run_score([["Q1", "x", "", "0", "", ""]], [])
        with self.assertRaises(SystemExit):
            self.run_score([["Q1", "x", "1", "0", "", ""], ["Q1", "x", "2", "0", "", ""]], [])

    def test_bad_tolerance_stops(self):
        with self.assertRaises(SystemExit):
            self.run_score([["Q1", "x", "1", "-1", "", ""]], [])

    def test_percent_tolerance_needs_a_percent_sign(self):
        with self.assertRaises(SystemExit):
            self.run_score([["Q1", "x", "2.4%", "0.1", "", ""]], [])
        code, _, v = self.run_score([["Q1", "x", "2.4%", "0.1%", "", ""]], [["Q1", "x", "2.45%", "", "", ""]])
        self.assertEqual(v["Q1"], "right")

    def test_example_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n in ("answer_key.csv", "ai_answers.csv"):
                Path(tmp, n).write_bytes((ROOT / "example" / n).read_bytes())
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(score.main([str(Path(tmp, "answer_key.csv")), str(Path(tmp, "ai_answers.csv"))]), 0)
        self.assertIn("Wrong:     3", out.getvalue())

    def test_templates_have_every_question(self):
        ids = [r["id"] for r in csv.DictReader(open(ROOT / "answer_key.csv"))]
        self.assertEqual(ids, [r["id"] for r in csv.DictReader(open(ROOT / "ai_answers.csv"))])
        text = (ROOT / "QUESTIONS.md").read_text()
        for n in range(1, 13):
            self.assertIn("| Q%02d |" % n, text)


if __name__ == "__main__":
    unittest.main()
