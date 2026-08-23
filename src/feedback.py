from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

FEEDBACK_FILE = (
    PROJECT_ROOT
    / "data"
    / "feedback"
    / "investigator_feedback.csv"
)


REQUIRED_FEEDBACK_COLUMNS = {
    "case_id",
    "feedback_type",
    "reason",
    "signal_category",
    "action",
}


def load_feedback(
    path: Path = FEEDBACK_FILE,
) -> pd.DataFrame:
    """Load investigator feedback."""

    if not path.exists():
        return pd.DataFrame(
            columns=sorted(REQUIRED_FEEDBACK_COLUMNS)
        )

    feedback = pd.read_csv(path)

    missing_columns = (
        REQUIRED_FEEDBACK_COLUMNS
        - set(feedback.columns)
    )

    if missing_columns:
        raise ValueError(
            "Feedback dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    return feedback


def build_signal_adjustments(
    feedback: pd.DataFrame,
) -> dict[str, float]:
    """
    Convert investigator feedback into signal-level adjustments.

    The adjustment is associated with a signal category rather
    than a specific case.
    """

    adjustments = {}

    if feedback.empty:
        return adjustments

    for _, row in feedback.iterrows():

        category = row["signal_category"]
        action = row["action"]

        if action == "exclude_from_risk":
            adjustments[category] = 0.0

        elif action == "downweight":
            adjustments[category] = 0.5

        elif action == "upweight":
            adjustments[category] = 1.25

    return adjustments


def apply_feedback(
    ranked_cases: pd.DataFrame,
    feedback: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply investigator feedback to the ranking.

    Feedback modifies signal contribution rather than
    removing individual cases from the ranking.
    """

    result = ranked_cases.copy()

    if feedback.empty:
        result["feedback_adjustment"] = 0.0
        result["adjusted_score"] = result[
            "investigation_score"
        ]

        result["rank_after_feedback"] = (
            result["adjusted_score"]
            .rank(
                method="first",
                ascending=False,
            )
            .astype(int)
        )

        return result

    adjustments = build_signal_adjustments(
        feedback
    )

    result["adjusted_score"] = (
        result["investigation_score"]
    )

    # ---------------------------------------------------------
    # Administrative activity
    #
    # This category is intentionally excluded from the base
    # financial risk score. Therefore feedback about this
    # category should not create a new financial penalty.
    # ---------------------------------------------------------

    if "administrative_activity" in adjustments:

        # No financial signal is associated with this category.
        # We retain the feedback as governance information.
        pass

    # ---------------------------------------------------------
    # Future signal-level adjustments
    #
    # These categories can be mapped to actual signal columns
    # as the feedback dataset grows.
    # ---------------------------------------------------------

    signal_mapping = {
        "payment_deviation": "award_deviation_signal",
        "persistence": "persistence_signal",
        "duplicate_payment": "duplicate_payment_signal",
        "multiple_payment": "multiple_payment_signal",
        "temporal_change": "monthly_change_signal",
    }

    for category, multiplier in adjustments.items():

        signal_column = signal_mapping.get(category)

        if signal_column is None:
            continue

        if signal_column not in result.columns:
            continue

        # Recalculate the contribution associated with this
        # signal rather than applying a case-specific penalty.
        result["adjusted_score"] = (
            result["adjusted_score"]
            - result[signal_column]
            + result[signal_column] * multiplier
        )

    result["feedback_adjustment"] = (
        result["adjusted_score"]
        - result["investigation_score"]
    )

    result["adjusted_score"] = (
        result["adjusted_score"]
        .clip(lower=0.0)
    )

    result = (
        result
        .sort_values(
            by=[
                "adjusted_score",
                "investigation_score",
            ],
            ascending=False,
        )
        .reset_index(drop=True)
    )

    result["rank_after_feedback"] = (
        result.index + 1
    )

    return result
