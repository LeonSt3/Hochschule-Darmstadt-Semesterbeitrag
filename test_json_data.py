import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable, Iterable

import pytest

# Quelle der Wahrheit im Repo
HISTORY_PATH = Path(__file__).parent / "data" / "history.json"

# Test-Datensätze
HISTORY_PATH_HAPPY_PATH = Path(__file__).parent / "test_data" / "history_happy_path.json"
HISTORY_PATH_SHOULD_FAIL = Path(__file__).parent / "test_data" / "history_data_should_fail.json"


def _load_history(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _to_cents(value) -> int:
    # robust gegen Float-Artefakte; rundet kaufmännisch auf 2 Nachkommastellen
    d = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)


def _extract_semester_prefix(total: str) -> str | None:
    """
    Robustere Erkennung des führenden Semester-Tokens im 'total'-Text.

    Akzeptiert u.a.:
      - "Sommersemester 2023: ..."
      - "Wintersemester 2024/25 - ..."
      - "WS 2024/25: ..."
      - "SS 2023 ..."
    """
    s = (total or "").strip()

    m = re.match(
        r"""^\s*(
            (?:Sommer|Winter)semester\s+\d{4}(?:/\d{2,4})?
          | (?:SS|WS)\s+\d{4}(?:/\d{2,4})?
        )\b""",
        s,
        flags=re.IGNORECASE | re.VERBOSE,
    )
    if not m:
        return None

    token = m.group(1).strip()

    # Normalisiere Abkürzungen auf ausgeschriebene Form, damit Vergleich stabil ist.
    # Wichtig: keine Inline-Flags wie (?i) verwenden (Python: "global flags not at the start").
    if re.match(r"^SS\b", token, flags=re.IGNORECASE):
        token = re.sub(r"^SS\b", "Sommersemester", token, flags=re.IGNORECASE)
    elif re.match(r"^WS\b", token, flags=re.IGNORECASE):
        token = re.sub(r"^WS\b", "Wintersemester", token, flags=re.IGNORECASE)

    # Whitespace normalisieren
    token = re.sub(r"\s+", " ", token)
    return token


def _validate_no_calculation_errors(history) -> list[str]:
    errors: list[str] = []

    for entry in history:
        semester = entry.get("semester")
        total_value = entry.get("total_value")
        items = entry.get("items", [])

        if total_value is None:
            errors.append(f"{semester}: total_value fehlt")
            continue

        items_sum_cents = sum(_to_cents(it.get("value", 0)) for it in items)
        total_cents = _to_cents(total_value)

        # Toleranz: 1 Cent
        if abs(total_cents - items_sum_cents) > 1:
            errors.append(
                f"{semester}: total_value={total_value} (={total_cents}ct) "
                f"!= Summe(items.value)={items_sum_cents / 100:.2f} (={items_sum_cents}ct)"
            )

    return errors


def _validate_semester_matches_total_prefix(history) -> list[str]:
    errors: list[str] = []

    for entry in history:
        semester = entry.get("semester", "").strip()
        total = entry.get("total", "")

        extracted = _extract_semester_prefix(total)
        if extracted is None:
            errors.append(f"{semester}: Konnte Semester nicht aus total extrahieren: {total!r}")
            continue

        # Vergleich case-insensitive + normalisierte Whitespaces
        norm_semester = re.sub(r"\s+", " ", semester).strip().lower()
        norm_extracted = re.sub(r"\s+", " ", extracted).strip().lower()

        if norm_extracted != norm_semester:
            errors.append(f"{semester}: total beginnt mit {extracted!r}")

    return errors


_AMOUNT_EUR_RE = re.compile(r"(\d+(?:[.,]\d{1,2})?)\s*€")


def _extract_first_eur_amount_to_cents(text: str) -> int | None:
    m = _AMOUNT_EUR_RE.search(text or "")
    if not m:
        return None
    val = Decimal(m.group(1).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(val * 100)


def _validate_basic_schema(history) -> list[str]:
    errors: list[str] = []
    if not isinstance(history, list):
        return ["Root: muss eine Liste sein"]

    required_entry_keys = {"source", "fetched_at", "semester", "total", "total_value", "items"}
    required_item_keys = {"name", "amount", "value"}

    for i, entry in enumerate(history):
        if not isinstance(entry, dict):
            errors.append(f"[{i}]: entry muss ein Objekt sein")
            continue

        missing = required_entry_keys - set(entry.keys())
        if missing:
            errors.append(f"[{i}] {entry.get('semester')}: fehlende Keys: {sorted(missing)}")

        if not isinstance(entry.get("items"), list):
            errors.append(f"[{i}] {entry.get('semester')}: items muss Liste sein")
            continue

        for j, item in enumerate(entry["items"]):
            if not isinstance(item, dict):
                errors.append(f"[{i}] {entry.get('semester')} items[{j}]: item muss Objekt sein")
                continue
            missing_item = required_item_keys - set(item.keys())
            if missing_item:
                errors.append(
                    f"[{i}] {entry.get('semester')} items[{j}]: fehlende Keys: {sorted(missing_item)}"
                )

    return errors


def _validate_total_amount_matches_total_value(history) -> list[str]:
    errors: list[str] = []
    for entry in history:
        semester = entry.get("semester")
        total = entry.get("total", "")
        total_value = entry.get("total_value")

        if total_value is None:
            continue

        total_amount_cents = _extract_first_eur_amount_to_cents(total)
        if total_amount_cents is None:
            errors.append(f"{semester}: Konnte Betrag nicht aus total extrahieren: {total!r}")
            continue

        if abs(total_amount_cents - _to_cents(total_value)) > 1:
            errors.append(
                f"{semester}: total Betrag {total_amount_cents / 100:.2f} != total_value {total_value}"
            )
    return errors


def _validate_item_amount_matches_item_value(history) -> list[str]:
    errors: list[str] = []
    for entry in history:
        semester = entry.get("semester")
        for item in entry.get("items", []):
            name = item.get("name")
            amount = item.get("amount", "")
            value = item.get("value")
            if value is None:
                errors.append(f"{semester} - {name}: value fehlt")
                continue
            amount_cents = _extract_first_eur_amount_to_cents(amount)
            if amount_cents is None:
                errors.append(f"{semester} - {name}: Konnte Betrag nicht aus amount extrahieren: {amount!r}")
                continue
            if abs(amount_cents - _to_cents(value)) > 1:
                errors.append(
                    f"{semester} - {name}: amount {amount_cents / 100:.2f} != value {value}"
                )
    return errors


def _validate_no_negative_values(history) -> list[str]:
    errors: list[str] = []
    for entry in history:
        semester = entry.get("semester")
        if entry.get("total_value", 0) < 0:
            errors.append(f"{semester}: total_value negativ")
        for item in entry.get("items", []):
            if item.get("value", 0) < 0:
                errors.append(f"{semester} - {item.get('name')}: value negativ")
    return errors


# --- Test Helpers ---


HistoryType = list[dict[str, Any]]
ValidatorFn = Callable[[HistoryType], list[str]]


@dataclass(frozen=True)
class Validator:
    name: str
    category: str
    fn: ValidatorFn


VALIDATORS: tuple[Validator, ...] = (
    Validator("schema", "schema", _validate_basic_schema),
    Validator("calculation", "calc", _validate_no_calculation_errors),
    Validator("semester_total_prefix", "semester", _validate_semester_matches_total_prefix),
    Validator("total_amount_vs_total_value", "amount", _validate_total_amount_matches_total_value),
    Validator("item_amount_vs_item_value", "amount", _validate_item_amount_matches_item_value),
    Validator("no_negative_values", "sanity", _validate_no_negative_values),
)


def _run_validators_safely(history: HistoryType, validators: Iterable[Validator] = VALIDATORS) -> dict[str, list[str]]:
    """Führt Validatoren aus und garantiert: nie Exceptions nach außen.

    Rückgabe: mapping validator_name -> liste von error-strings (leer wenn ok)
    """
    results: dict[str, list[str]] = {}
    for v in validators:
        try:
            results[v.name] = v.fn(history) or []
        except Exception as e:  # pragma: no cover
            results[v.name] = [f"EXCEPTION in {v.name}: {type(e).__name__}: {e}"]
    return results


def _flatten_errors(results: dict[str, list[str]]) -> list[str]:
    out: list[str] = []
    for name, errs in results.items():
        for err in errs:
            out.append(f"[{name}] {err}")
    return out


def _categories_with_errors(results: dict[str, list[str]]) -> set[str]:
    name_to_category = {v.name: v.category for v in VALIDATORS}
    cats: set[str] = set()
    for name, errs in results.items():
        if errs:
            cats.add(name_to_category.get(name, "unknown"))
    return cats


def _assert_no_errors(results: dict[str, list[str]], *, context: str):
    all_errors = _flatten_errors(results)
    assert not all_errors, context + "\n" + "\n".join(all_errors)


def _assert_has_error_categories(results: dict[str, list[str]], *, expected_categories: set[str], context: str):
    cats = _categories_with_errors(results)
    missing = expected_categories - cats
    assert not missing, (
            context
            + "\nExpected error categories missing: "
            + ", ".join(sorted(missing))
            + "\nGot categories: "
            + ", ".join(sorted(cats))
            + "\nErrors:\n"
            + "\n".join(_flatten_errors(results))
    )


# --- Fixtures ---


@pytest.fixture(scope="session")
def history_prod():
    return _load_history(HISTORY_PATH)


@pytest.fixture(scope="session")
def history_happy():
    return _load_history(HISTORY_PATH_HAPPY_PATH)


@pytest.fixture(scope="session")
def history_should_fail():
    return _load_history(HISTORY_PATH_SHOULD_FAIL)


# --- Parametrisierte Tests ---


@pytest.mark.parametrize(
    "dataset_name,fixture_name",
    [
        ("prod", "history_prod"),
        ("happy", "history_happy"),
    ],
)
def test_dataset_has_no_validation_errors(request, dataset_name: str, fixture_name: str):
    """Diese Tests sind die 'Gatekeeper' für eine Pipeline.

    PROD ist die Quelle der Wahrheit: wenn hier Errors auftauchen, sind die Daten inkonsistent/unvollständig
    und die Pipeline soll bewusst failen.
    """
    history = request.getfixturevalue(fixture_name)
    results = _run_validators_safely(history)

    exception_lines = [e for e in _flatten_errors(results) if "EXCEPTION" in e]
    assert not exception_lines, (
            f"{dataset_name}: Validator darf keine Exceptions werfen.\n" + "\n".join(exception_lines)
    )

    _assert_no_errors(results, context=f"{dataset_name}: Validierungsfehler gefunden (Pipeline soll failen)")


def test_should_fail_has_expected_error_categories(history_should_fail):
    """Der Should-Fail-Datensatz soll gezielt mehrere Fehlerklassen abdecken."""
    results = _run_validators_safely(history_should_fail)

    exception_lines = [e for e in _flatten_errors(results) if "EXCEPTION" in e]
    assert not exception_lines, (
            "should_fail: Validator darf keine Exceptions werfen.\n" + "\n".join(exception_lines)
    )

    _assert_has_error_categories(
        results,
        expected_categories={"calc", "semester"},
        context="should_fail: Expected bestimmte Fehlerkategorien",
    )
