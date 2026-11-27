"""Validate a data migration by comparing a legacy CSV export to the migrated CSV.

Checks:
  * row counts
  * records missing from / unexpectedly added to the target (matched on a key column)
  * duplicate keys on either side
  * field-level mismatches (after normalising whitespace, case for text columns
    and numeric formatting)
  * required fields that are empty in the target

Exit code is 0 when the migration is clean and 1 when problems are found, so it
can gate a CI job or a cutover checklist.

Usage:
    python validator.py legacy.csv migrated.csv --key id --required name email
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


def normalise(value: str | None, numeric: bool = False) -> str:
    text = (value or "").strip()
    if numeric and text:
        try:
            return format(Decimal(text.replace(",", "")).normalize(), "f")
        except InvalidOperation:
            return text
    return " ".join(text.split()).casefold()


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def duplicates(rows: list[dict], key: str) -> list[str]:
    counts = Counter(r[key] for r in rows)
    return sorted(k for k, n in counts.items() if n > 1)


def validate(legacy, target, key, required=(), numeric=()):
    """Compare two lists of row dicts. Returns a dict of findings."""
    findings = {
        "row_counts": {"legacy": len(legacy), "target": len(target)},
        "missing_in_target": [],
        "unexpected_in_target": [],
        "duplicate_keys_legacy": duplicates(legacy, key),
        "duplicate_keys_target": duplicates(target, key),
        "mismatches": [],
        "empty_required": [],
    }
    legacy_by_key = {r[key]: r for r in legacy}
    target_by_key = {r[key]: r for r in target}

    findings["missing_in_target"] = sorted(legacy_by_key.keys() - target_by_key.keys())
    findings["unexpected_in_target"] = sorted(target_by_key.keys() - legacy_by_key.keys())

    shared_columns = [c for c in legacy[0].keys() if c in (target[0].keys() if target else [])] if legacy else []
    for k in sorted(legacy_by_key.keys() & target_by_key.keys()):
        for col in shared_columns:
            if col == key:
                continue
            is_num = col in numeric
            a = normalise(legacy_by_key[k].get(col), is_num)
            b = normalise(target_by_key[k].get(col), is_num)
            if a != b:
                findings["mismatches"].append(
                    {"key": k, "column": col, "legacy": legacy_by_key[k].get(col), "target": target_by_key[k].get(col)}
                )

    for row in target:
        for col in required:
            if not (row.get(col) or "").strip():
                findings["empty_required"].append({"key": row[key], "column": col})
    return findings


def is_clean(f: dict) -> bool:
    return (
        f["row_counts"]["legacy"] == f["row_counts"]["target"]
        and not f["missing_in_target"]
        and not f["unexpected_in_target"]
        and not f["duplicate_keys_legacy"]
        and not f["duplicate_keys_target"]
        and not f["mismatches"]
        and not f["empty_required"]
    )


def render(f: dict) -> str:
    out = ["# Migration validation report", ""]
    rc = f["row_counts"]
    out.append(f"- Row counts: legacy **{rc['legacy']}**, target **{rc['target']}**"
               + ("" if rc["legacy"] == rc["target"] else "  (MISMATCH)"))
    sections = [
        ("Missing in target", f["missing_in_target"]),
        ("Unexpected in target", f["unexpected_in_target"]),
        ("Duplicate keys in legacy", f["duplicate_keys_legacy"]),
        ("Duplicate keys in target", f["duplicate_keys_target"]),
    ]
    for title, items in sections:
        out.append(f"- {title}: {', '.join(items) if items else 'none'}")
    out += ["", f"## Field mismatches ({len(f['mismatches'])})"]
    out += [f"- `{m['key']}` / **{m['column']}**: legacy `{m['legacy']}` vs target `{m['target']}`" for m in f["mismatches"]] or ["None"]
    out += ["", f"## Empty required fields in target ({len(f['empty_required'])})"]
    out += [f"- `{e['key']}` / **{e['column']}**" for e in f["empty_required"]] or ["None"]
    out += ["", "**Result: " + ("PASS" if is_clean(f) else "FAIL") + "**"]
    return "\n".join(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("legacy", type=Path)
    p.add_argument("target", type=Path)
    p.add_argument("--key", required=True, help="column that uniquely identifies a record")
    p.add_argument("--required", nargs="*", default=[], help="columns that must not be empty in the target")
    p.add_argument("--numeric", nargs="*", default=[], help="columns compared as numbers (1,000.50 == 1000.5)")
    p.add_argument("-o", "--output", type=Path, help="write the Markdown report to this file")
    args = p.parse_args(argv)

    findings = validate(read_rows(args.legacy), read_rows(args.target), args.key, args.required, args.numeric)
    report = render(findings)
    if args.output:
        args.output.write_text(report + "\n")
    print(report)
    return 0 if is_clean(findings) else 1


if __name__ == "__main__":
    sys.exit(main())
