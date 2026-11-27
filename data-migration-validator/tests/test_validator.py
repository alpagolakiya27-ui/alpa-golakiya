import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import validator  # noqa: E402

LEGACY = [
    {"id": "1", "name": "Acme", "balance": "1,250.00"},
    {"id": "2", "name": "Birch", "balance": "10"},
]


def test_clean_migration_passes_with_formatting_differences():
    target = [
        {"id": "1", "name": "  acme ", "balance": "1250"},
        {"id": "2", "name": "Birch", "balance": "10.0"},
    ]
    f = validator.validate(LEGACY, target, "id", numeric=["balance"])
    assert validator.is_clean(f)


def test_missing_and_unexpected_records():
    target = [{"id": "1", "name": "Acme", "balance": "1250"}, {"id": "9", "name": "New", "balance": "1"}]
    f = validator.validate(LEGACY, target, "id", numeric=["balance"])
    assert f["missing_in_target"] == ["2"]
    assert f["unexpected_in_target"] == ["9"]


def test_field_mismatch_detected():
    target = [{"id": "1", "name": "Acme", "balance": "1205"}, {"id": "2", "name": "Birch", "balance": "10"}]
    f = validator.validate(LEGACY, target, "id", numeric=["balance"])
    assert len(f["mismatches"]) == 1
    assert f["mismatches"][0]["column"] == "balance"


def test_duplicates_and_empty_required():
    target = [
        {"id": "1", "name": "", "balance": "1250"},
        {"id": "1", "name": "", "balance": "1250"},
        {"id": "2", "name": "Birch", "balance": "10"},
    ]
    f = validator.validate(LEGACY, target, "id", required=["name"], numeric=["balance"])
    assert f["duplicate_keys_target"] == ["1"]
    assert len(f["empty_required"]) == 2
    assert not validator.is_clean(f)


def test_cli_exit_codes(tmp_path):
    sample = ROOT / "sample_data"
    bad = validator.main([str(sample / "legacy_customers.csv"), str(sample / "migrated_customers.csv"),
                          "--key", "id", "--required", "email", "--numeric", "balance"])
    assert bad == 1
    ok = validator.main([str(sample / "legacy_customers.csv"), str(sample / "legacy_customers.csv"), "--key", "id"])
    assert ok == 0
