# AI Code Evaluation Toolkit

A small Python tool for **grading and ranking AI-generated code** against a task
definition and a weighted rubric. It mirrors how code-evaluation and RLHF review
work: check each response against the requirements, hunt for edge cases, compare
responses and explain the reasoning.

## What it does

- Runs each candidate solution in an **isolated subprocess with a timeout**, so
  infinite loops, crashes and import-time errors are reported rather than hanging
  the evaluator
- Scores each candidate on three weighted rubric dimensions
  - **Correctness:** visible test cases
  - **Edge cases:** hidden or tricky inputs such as empty strings and invalid types
  - **Quality:** docstring, type hints, no stray `print()` calls (static checks via `ast`)
- Ranks candidates and writes a Markdown report listing every failure with the
  expected and actual values

## Quick start

```bash
pip install -r requirements.txt   # only pytest is needed
python evaluator.py tasks/is_palindrome.json candidates/is_palindrome/*.py
python evaluator.py tasks/is_palindrome.json candidates/is_palindrome/*.py -o report.md
pytest
```

Example output:

| Rank | Candidate | Correctness | Edge cases | Quality | Total |
|---|---|---|---|---|---|
| 1 | response_a | 100% | 100% | 100% | **100.0** |
| 2 | response_c | 100% | 67% | 70% | **84.0** |
| 3 | response_b | 50% | 67% | 30% | **51.0** |

See [`examples/sample_written_evaluation.md`](examples/sample_written_evaluation.md)
for the matching human-written rationale.

## Adding your own task

Create a JSON file in `tasks/`:

```json
{
  "function": "my_func",
  "prompt": "What the model was asked to do",
  "weights": {"correctness": 0.5, "edge_cases": 0.3, "quality": 0.2},
  "cases": [
    {"args": [1, 2], "expected": 3, "kind": "visible"},
    {"args": [null], "raises": "TypeError", "kind": "edge"}
  ]
}
```

Then drop candidate `.py` files in `candidates/<task>/` and run the evaluator.

## Notes and limits

- The subprocess gives timeout and crash isolation, **not a security sandbox**.
  Only run code you are willing to execute on your own machine.
- Quality checks are deliberately simple heuristics. The written rationale is
  where human judgement goes.

## Skills demonstrated

Python · subprocess isolation · AST analysis · rubric design · pytest · technical writing
