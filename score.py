#!/usr/bin/env python3
"""Score an AI's figures against your own answer key, and count the wrong ones.

    python3 score.py answer_key.csv ai_answers.csv

Writes results.csv next to ai_answers.csv (results-2.csv and so on if one exists; it never overwrites)
and prints the counts. Standard library only.
"""
import csv
import re
import sys
from decimal import Decimal
from pathlib import Path

CAUSES = ("definition", "time window", "double counted", "filter", "missing data", "other")
WORDS = {"up", "down", "same"}
# One figure: optional minus or brackets, optional currency sign, digits with commas, optional % or k/m/b.
_NUM = re.compile(r"^(\()?(-)?([$£€])?(-)?(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)(%|k|m|b)?(\))?$")
_SCALE = {"%": Decimal("0.01"), "k": Decimal(1000), "m": Decimal(1000000), "b": Decimal(1000000000)}


def currency(text):
    """The currency sign written with a figure, or '' when none."""
    m = _NUM.match((text or "").strip().lower())
    return (m.group(3) or "") if m else ""


def parse_figure(text):
    """Return a Decimal, one of WORDS, or None when the cell holds no single figure.
    A percent is stored as a fraction, so 38.5% and 0.385 are the same figure.
    A space inside the cell means more than one figure, so it is not read as one."""
    s = (text or "").strip().lower()
    if s in WORDS:
        return s
    m = _NUM.match(s)
    if not m or bool(m.group(1)) != bool(m.group(7)) or (m.group(2) and m.group(4)):
        return None
    value = Decimal(m.group(5).replace(",", ""))
    if m.group(6):
        value *= _SCALE[m.group(6)]
    return -value if (m.group(1) or m.group(2) or m.group(4)) else value


def matches(true, ai, tolerance):
    """True when the AI figure equals the right one within the tolerance (an absolute amount)."""
    if isinstance(true, str) or isinstance(ai, str):
        return true == ai
    return abs(true - ai) <= tolerance


def cell(text):
    """Text for results.csv that a spreadsheet will show as text, never run as a formula."""
    text = text or ""
    if text[:1] in ("=", "+", "@", "\t", "\r") or (text[:1] == "-" and parse_figure(text) is None):
        return "'" + text
    return text


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    ids = [r.get("id", "").strip() for r in rows]
    dupes = sorted({i for i in ids if i and ids.count(i) > 1})
    if dupes:
        raise SystemExit("%s: these ids appear more than once: %s" % (path, ", ".join(dupes)))
    return {r["id"].strip(): r for r in rows if r.get("id", "").strip()}


def score(key_path, answers_path):
    key, answers = read(key_path), read(answers_path)
    results = []
    for qid, k in key.items():
        true = parse_figure(k.get("right_figure"))
        if true is None:
            raise SystemExit("%s: %s has no right figure. Fill it in, or remove the row." % (key_path, qid))
        tol = parse_figure(k.get("tolerance") or "0")
        if not isinstance(tol, Decimal) or tol < 0:
            raise SystemExit("%s: %s has a tolerance that is not a number of zero or more." % (key_path, qid))
        if "%" in (k.get("right_figure") or "") and tol and "%" not in (k.get("tolerance") or ""):
            # 0.1 next to 2.4% would mean ten percentage points and pass almost any answer
            raise SystemExit("%s: %s is a percent, so write its tolerance with a %% sign, for example 0.1%%."
                             % (key_path, qid))
        a = answers.get(qid)
        if a is None:
            verdict, ai = "not asked", None
        else:
            if (a.get("question") or "").strip() != (k.get("question") or "").strip():
                raise SystemExit("%s: the question words differ between the two files. Use the same words." % qid)
            ai = parse_figure(a.get("ai_figure"))
            if ai is None:
                verdict = "no figure"
            else:
                ck, ca = currency(k.get("right_figure")), currency(a.get("ai_figure"))
                same_money = not (ck and ca) or ck == ca  # $100 and €100 are different figures
                verdict = "right" if same_money and matches(true, ai, tol) else "wrong"
        results.append({"id": qid, "question": cell(k.get("question")), "right_figure": cell(k.get("right_figure")),
                        "ai_figure": cell((a or {}).get("ai_figure")), "verdict": verdict,
                        "definition": cell(k.get("definition")), "cause": ""})
    extra = sorted(set(answers) - set(key))
    return results, extra


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    results, extra = score(argv[0], argv[1])
    folder = Path(argv[1]).parent
    for n in range(1, 1000):  # never overwrite: an earlier results file may hold causes you wrote in it
        out = folder / ("results.csv" if n == 1 else "results-%d.csv" % n)
        try:
            f = open(out, "x", newline="", encoding="utf-8")
            break
        except FileExistsError:
            continue
    else:
        raise SystemExit("Too many results files in %s. Move some away and run again." % folder)
    with f:
        w = csv.DictWriter(f, fieldnames=list(results[0]) if results else ["id"])
        w.writeheader()
        w.writerows(results)
    n = {v: sum(r["verdict"] == v for r in results) for v in ("right", "wrong", "no figure", "not asked")}
    checked = n["right"] + n["wrong"] + n["no figure"]
    print("Figures checked: %d" % checked)
    print("  Right:     %d" % n["right"])
    print("  Wrong:     %d" % n["wrong"])
    print("  No figure: %d (the AI gave no single figure)" % n["no figure"])
    if n["not asked"]:
        print("Not asked:   %d" % n["not asked"])
    if extra:
        print("Ignored, not in the answer key: %s" % ", ".join(extra))
    print("\nResults: %s" % out)
    if n["wrong"] or n["no figure"]:
        print("Next: for each wrong figure, write its cause in the 'cause' column: %s." % ", ".join(CAUSES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
