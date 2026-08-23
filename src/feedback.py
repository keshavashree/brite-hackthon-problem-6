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
    """
    Load investigator feedback.

    Feedback is external to the core ranking model so that
    investigator knowledge can be incorporated without
    retraining the underlying scoring system.
    """

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


def apply_feedback(
    ranked_cases: pd.DataFrame,
    feedback: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply investigator feedback to an existing ranking.

    This function does NOT retrain the model.

    It adjusts the investigation score based on documented
    investigator feedback.
    """

    result = ranked_cases.copy()

    if feedback.empty:
        return result

    result["feedback_adjustment"] = 0.0

    # ---------------------------------------------------------
    # Administrative activity feedback
    #
    # The Surprise Challenge showed that administrative activity
    # should not itself be treated as evidence of improper payment.
    # ---------------------------------------------------------

    administrative_feedback = feedback[
        (
            feedback["signal_category"]
            == "administrative_activity"
        )
        & (
            feedback["action"]
            == "downweight"
        )
    ]

    if not administrative_feedback.empty:

        affected_cases = set(
            administrative_feedback["case_id"]
        )

        mask = result["case_id"].isin(
            affected_cases
        )

        # Administrative activity is not part of our base
        # financial score. Therefore this adjustment acts as
        # a conservative penalty for previously referred cases
        # whose referral was determined to be administrative.
        result.loc[
            mask,
            "feedback_adjustment",
        ] = -0.25

    result["adjusted_score"] = (
        result["investigation_score"]
        + result["feedback_adjustment"]
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
