from pathlib import Path
import pandas as pd


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

CASES_FILE = DATA_DIR / "cases.csv"
PAYMENTS_FILE = DATA_DIR / "payments.csv"


REQUIRED_CASE_COLUMNS = {
    "case_id",
    "district",
    "household_size",
    "age_band",
    "language_preference",
    "tenure",
    "opened_date",
    "status",
    "closure_month",
    "monthly_award",
    "payment_adjustments",
    "contact_attempts",
    "months_since_review",
}

REQUIRED_PAYMENT_COLUMNS = {
    "payment_id",
    "case_id",
    "pay_month",
    "amount",
    "method",
    "adjustment",
}


class DataValidationError(Exception):
    """Raised when the supplied data fails validation."""


def load_cases(path: Path = CASES_FILE) -> pd.DataFrame:
    """Load and validate the cases dataset."""

    if not path.exists():
        raise FileNotFoundError(f"Cases file not found: {path}")

    cases = pd.read_csv(path)

    missing_columns = REQUIRED_CASE_COLUMNS - set(cases.columns)

    if missing_columns:
        raise DataValidationError(
            f"Cases dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if cases["case_id"].duplicated().any():
        duplicates = cases.loc[
            cases["case_id"].duplicated(),
            "case_id"
        ].tolist()

        raise DataValidationError(
            f"Duplicate case_id values found: {duplicates[:10]}"
        )

    if cases["monthly_award"].isna().any():
        raise DataValidationError(
            "Cases dataset contains missing monthly_award values."
        )

    return cases


def load_payments(path: Path = PAYMENTS_FILE) -> pd.DataFrame:
    """Load and validate the payments dataset."""

    if not path.exists():
        raise FileNotFoundError(f"Payments file not found: {path}")

    payments = pd.read_csv(path)

    missing_columns = REQUIRED_PAYMENT_COLUMNS - set(payments.columns)

    if missing_columns:
        raise DataValidationError(
            f"Payments dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    if payments["payment_id"].duplicated().any():
        duplicates = payments.loc[
            payments["payment_id"].duplicated(),
            "payment_id"
        ].tolist()

        raise DataValidationError(
            f"Duplicate payment_id values found: {duplicates[:10]}"
        )

    if payments["amount"].isna().any():
        raise DataValidationError(
            "Payments dataset contains missing amount values."
        )

    if (payments["amount"] <= 0).any():
        raise DataValidationError(
            "Payments dataset contains zero or negative amounts."
        )

    return payments


def validate_case_payment_relationship(
    cases: pd.DataFrame,
    payments: pd.DataFrame,
) -> None:
    """Ensure every payment belongs to a known case."""

    known_cases = set(cases["case_id"])

    payment_cases = set(payments["case_id"])

    unknown_cases = payment_cases - known_cases

    if unknown_cases:
        raise DataValidationError(
            "Payments reference unknown case IDs: "
            f"{sorted(unknown_cases)[:10]}"
        )


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load both datasets and perform cross-dataset validation.

    Returns:
        cases, payments
    """

    cases = load_cases()
    payments = load_payments()

    validate_case_payment_relationship(cases, payments)

    return cases, payments