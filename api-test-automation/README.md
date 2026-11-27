# REST API Test Automation (pytest)

An automated regression suite for a small inventory REST API, built with
**pytest** and **requests**. The API is included (standard library only) so the
project runs anywhere with no external services.

I built this to show the habits from nine years in QA automation: isolated tests,
data-driven edge cases, a smoke subset for fast pre-release checks, and CI.

## Highlights

- **Isolated tests:** a fixture starts a fresh server on a free port for every
  test, so tests never depend on each other's data
- **Data-driven validation:** `pytest.mark.parametrize` covers missing fields,
  empty and whitespace names, wrong types, negative quantities, malformed JSON
  and non-object bodies
- **Classic edge cases:** `True` passes as an `int` in Python, so a boolean
  `quantity` is explicitly tested and rejected
- **Smoke vs full regression:** `pytest -m smoke` runs the fast subset, while
  `pytest` runs everything
- **CI:** a GitHub Actions workflow runs smoke tests, then the full suite, on every push

## API under test

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/items` | 200 list | |
| GET | `/items/{id}` | 200 item | 404 |
| POST | `/items` | 201 item | 400 validation |
| DELETE | `/items/{id}` | 204 | 404 |

Item shape: `{"id": int, "name": non-empty string, "quantity": int >= 0}`

## Run it

```bash
pip install -r requirements.txt
pytest -v             # full regression
pytest -m smoke       # smoke only
python -m app.server  # run the API yourself on :8000
```

## Structure

```
app/server.py            API under test
tests/conftest.py        server + client fixtures
tests/test_items_api.py  test cases
.github/workflows/       CI
```

## Skills demonstrated

pytest · REST API testing · test design (boundary values, negative testing) · fixtures · CI with GitHub Actions
