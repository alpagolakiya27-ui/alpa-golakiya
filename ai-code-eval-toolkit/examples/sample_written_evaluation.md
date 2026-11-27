# Sample written evaluation (human rationale)

This is the kind of written feedback an AI-training or RLHF task asks for, in
addition to the automated scores. It evaluates the three responses in
`candidates/is_palindrome/` against the prompt in `tasks/is_palindrome.json`.

**Prompt requirements:** ignore case and non-alphanumerics, return a bool,
raise `TypeError` on non-string input.

## Ranking: A > C > B

### Response A: best
Meets every requirement. It validates input type first, normalises with a regex
and compares to the reverse. The empty string correctly returns `True`. It has a
docstring and type hints and no side effects. The only thing I would still
mention is that it builds a full reversed copy, which is fine here and keeps the
code easy to read.

### Response C: acceptable logic, one real bug and one hygiene problem
The normalisation and type check are right, and all the visible cases pass. But:
1. **Bug:** `if len(chars) == 0: return False`. An empty or punctuation-only
   string is conventionally a palindrome. The prompt's "ignore non-alphanumerics"
   rule makes `" "` and `"."` reduce to empty, so these inputs return the wrong
   answer.
2. **Hygiene:** a leftover `print("checking", chars)` writes to stdout on every
   call, which would pollute logs or break callers that parse output.

### Response B: does not meet the prompt
`s == s[::-1]` ignores two of the three requirements. `"A man, a plan, a canal:
Panama"` returns `False`, and `None` raises `TypeError: 'NoneType' object is not
subscriptable` only by accident, with a message unrelated to the intent. No type
hints, no docstring.

## Why this ordering
Correctness against the stated requirements comes first, so B is last even though
it is the shortest. A and C differ in one bug and one hygiene issue, so A is
clearly better but C is not a failure.
