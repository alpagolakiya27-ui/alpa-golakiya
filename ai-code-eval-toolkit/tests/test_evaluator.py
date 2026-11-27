import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import evaluator  # noqa: E402

TASK = json.loads((ROOT / "tasks" / "is_palindrome.json").read_text())
CAND = ROOT / "candidates" / "is_palindrome"


def score(name):
    return evaluator.evaluate(CAND / f"{name}.py", TASK, TASK["weights"])


def test_good_candidate_scores_perfectly():
    ev = score("response_a")
    assert ev.total == 100.0
    assert not ev.failures


def test_naive_candidate_fails_visible_cases():
    ev = score("response_b")
    assert ev.scores["correctness"] < 1.0
    assert any(f.kind == "visible" for f in ev.failures)


def test_edge_case_bug_is_detected_and_print_flagged():
    ev = score("response_c")
    assert ev.scores["correctness"] == 1.0
    assert ev.scores["edge_cases"] < 1.0
    assert "contains print() calls" in ev.notes


def test_ranking_order():
    totals = {n: score(n).total for n in ("response_a", "response_b", "response_c")}
    assert totals["response_a"] > totals["response_c"] > totals["response_b"]


def test_timeout_is_handled(tmp_path):
    slow = tmp_path / "slow.py"
    slow.write_text("def is_palindrome(s):\n    while True:\n        pass\n")
    ev = evaluator.evaluate(slow, TASK, TASK["weights"], timeout=1)
    assert ev.scores["correctness"] == 0.0
    assert any("timed out" in n for n in ev.notes)


def test_missing_function_is_handled(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("def other():\n    return 1\n")
    ev = evaluator.evaluate(bad, TASK, TASK["weights"])
    assert ev.total == 0.0
