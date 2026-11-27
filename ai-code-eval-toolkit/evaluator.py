"""Rubric-based evaluator for AI-generated code.

Given a task definition (function name + test cases) and several candidate
solutions, it runs each candidate in an isolated subprocess with a timeout,
scores it against a weighted rubric, ranks the candidates and writes a
Markdown report.

Usage:
    python evaluator.py tasks/is_palindrome.json candidates/is_palindrome/*.py
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_WEIGHTS = {"correctness": 0.5, "edge_cases": 0.3, "quality": 0.2}

# Executed in a child process: loads the candidate file, runs every case and
# prints a JSON list of results. `-I` keeps the child out of the cwd/site dirs.
RUNNER = r"""
import importlib.util, json, sys
path, func_name, cases = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
spec = importlib.util.spec_from_file_location("candidate", path)
mod = importlib.util.module_from_spec(spec)
results = []
try:
    spec.loader.exec_module(mod)
    func = getattr(mod, func_name)
except Exception as exc:
    print(json.dumps({"load_error": f"{type(exc).__name__}: {exc}"}))
    sys.exit(0)
for case in cases:
    try:
        actual = func(*case["args"])
        if "raises" in case:
            results.append({"ok": False, "detail": f"expected {case['raises']}, got {actual!r}"})
        else:
            ok = actual == case["expected"]
            results.append({"ok": ok, "detail": "" if ok else f"expected {case['expected']!r}, got {actual!r}"})
    except Exception as exc:
        if case.get("raises") == type(exc).__name__:
            results.append({"ok": True, "detail": ""})
        else:
            results.append({"ok": False, "detail": f"raised {type(exc).__name__}: {exc}"})
print(json.dumps({"results": results}))
"""


@dataclass
class CaseResult:
    kind: str
    args: list
    ok: bool
    detail: str


@dataclass
class Evaluation:
    name: str
    scores: dict = field(default_factory=dict)
    total: float = 0.0
    failures: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def run_cases(path: Path, func_name: str, cases: list[dict], timeout: int = 5):
    """Run all cases against one candidate. Returns (results, error_message)."""
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", RUNNER, str(path), func_name, json.dumps(cases)],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"timed out after {timeout}s"
    if proc.returncode != 0:
        return None, f"crashed: {proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else 'unknown error'}"
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return None, "produced no parseable output (does it print at import time?)"
    if "load_error" in payload:
        return None, payload["load_error"]
    return payload["results"], None


def quality_score(source: str, func_name: str) -> tuple[float, list[str]]:
    """Cheap static checks: docstring, type hints, no stray print calls."""
    notes: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return 0.0, [f"syntax error: {exc.msg}"]
    func = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == func_name), None)
    if func is None:
        return 0.0, [f"function `{func_name}` not found"]
    score = 0.0
    if ast.get_docstring(func):
        score += 0.4
    else:
        notes.append("missing docstring")
    if func.returns is not None and all(a.annotation is not None for a in func.args.args):
        score += 0.3
    else:
        notes.append("missing type hints")
    prints = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"]
    if prints:
        notes.append("contains print() calls")
    else:
        score += 0.3
    return score, notes


def evaluate(path: Path, task: dict, weights: dict, timeout: int = 5) -> Evaluation:
    ev = Evaluation(name=path.stem)
    cases = task["cases"]
    results, error = run_cases(path, task["function"], cases, timeout)
    q, q_notes = quality_score(path.read_text(), task["function"])
    ev.notes.extend(q_notes)
    ev.scores["quality"] = q

    if error:
        ev.scores.update(correctness=0.0, edge_cases=0.0)
        ev.notes.append(f"execution problem: {error}")
    else:
        for kind in ("correctness", "edge_cases"):
            wanted = "visible" if kind == "correctness" else "edge"
            picked = [(c, r) for c, r in zip(cases, results) if c.get("kind", "visible") == wanted]
            passed = sum(1 for _, r in picked if r["ok"])
            ev.scores[kind] = passed / len(picked) if picked else 1.0
            for c, r in picked:
                if not r["ok"]:
                    ev.failures.append(CaseResult(wanted, c["args"], False, r["detail"]))

    ev.total = round(sum(ev.scores[k] * weights[k] for k in weights) * 100, 1)
    return ev


def render_report(task: dict, evals: list[Evaluation], weights: dict) -> str:
    ranked = sorted(evals, key=lambda e: e.total, reverse=True)
    lines = [
        f"# Evaluation: `{task['function']}`",
        "",
        f"**Task:** {task['prompt']}",
        "",
        "**Rubric weights:** " + ", ".join(f"{k} {int(v * 100)}%" for k, v in weights.items()),
        "",
        "| Rank | Candidate | Correctness | Edge cases | Quality | Total |",
        "|---|---|---|---|---|---|",
    ]
    for i, e in enumerate(ranked, 1):
        s = e.scores
        lines.append(
            f"| {i} | {e.name} | {s['correctness']:.0%} | {s['edge_cases']:.0%} | {s['quality']:.0%} | **{e.total}** |"
        )
    lines.append("")
    for e in ranked:
        lines.append(f"## {e.name}")
        if not e.failures and not e.notes:
            lines.append("No issues found.")
        for f in e.failures:
            lines.append(f"- FAIL ({f.kind}) `{f.args}`: {f.detail}")
        for n in e.notes:
            lines.append(f"- Note: {n}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate candidate solutions against a task.")
    parser.add_argument("task", type=Path)
    parser.add_argument("candidates", type=Path, nargs="+")
    parser.add_argument("-o", "--output", type=Path, help="write the Markdown report here")
    parser.add_argument("--timeout", type=int, default=5)
    args = parser.parse_args(argv)

    task = json.loads(args.task.read_text())
    weights = task.get("weights", DEFAULT_WEIGHTS)
    evals = [evaluate(p, task, weights, args.timeout) for p in args.candidates]
    report = render_report(task, evals, weights)
    if args.output:
        args.output.write_text(report)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
