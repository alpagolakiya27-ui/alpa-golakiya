# Data Migration Validator

A command-line tool that checks whether a **legacy-system export** and the
**migrated data** actually match. Migrations such as legacy platform to ERP are
easy to get "mostly right" and costly to get wrong, so this tool turns the
validation step into something repeatable.

It uses only the Python standard library.

## What it checks

| Check | Why it matters |
|---|---|
| Row counts | Fast signal that records were dropped or duplicated |
| Missing / unexpected records | Matched on a key column such as customer ID |
| Duplicate keys (both sides) | Common result of re-running an import |
| Field-by-field mismatches | Catches changed values, not just missing rows |
| Required fields empty in target | Catches data that loads but breaks downstream workflows |

Comparison is **format-tolerant**: surrounding whitespace and case are ignored for
text, and columns passed to `--numeric` compare as numbers, so `1,250.00` equals
`1250`. Real differences are reported and formatting noise is not.

## Usage

```bash
python validator.py sample_data/legacy_customers.csv sample_data/migrated_customers.csv \
    --key id --required name email --numeric balance
```

The sample data has deliberately seeded problems and produces:

```
# Migration validation report

- Row counts: legacy 6, target 6
- Missing in target: 5, 6
- Unexpected in target: 7
- Duplicate keys in legacy: none
- Duplicate keys in target: 4

## Field mismatches (2)
- `3` / **email**: legacy `hello@cedar.example` vs target ``
- `4` / **balance**: legacy `9800` vs target `9080`      <- transposed digits

## Empty required fields in target (1)
- `3` / **email**

**Result: FAIL**
```

Notice that the row counts match (6 and 6) while the data does not. Counts alone
would have called this migration fine, which is why the other checks matter.

The exit code is `0` for a clean migration and `1` otherwise, so it can gate a
cutover checklist or CI job. Add `-o report.md` to save the report.

## Tests

```bash
pip install -r requirements.txt
pytest
```

## Skills demonstrated

Python · data validation · CSV processing · migration testing · CLI design · pytest
