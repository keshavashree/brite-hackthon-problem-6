import pandas as pd


def calculate_investigation_score(
    signals: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate an explainable investigation-prioritisation score.

    The score is not a probability of improper payment.
    It is used only to prioritise cases for human review.
    """

    result = signals.copy()

    # ---------------------------------------------------------
    # Signal weights
    #
    # These are deliberately based on financial/payment
    # behaviour rather than demographic or administrative
    # characteristics.
    # ---------------------------------------------------------

    result["investigation_score"] = (
        0.30 * result["award_deviation_signal"]
        + 0.25 * result["persistence_signal"]
        + 0.15 * result["severe_persistence_signal"]
        + 0.10 * result["extreme_deviation_signal"]
        + 0.10 * result["multiple_payment_signal"]
        + 0.05 * result["duplicate_payment_signal"]
        + 0.05 * result["monthly_change_signal"]
    )

    return result


def create_ranked_worklist(
    signals: pd.DataFrame,
    top_n: int | None = 20
) -> pd.DataFrame:
    """
    Create the ranked investigation worklist.

    Returns the top N cases by investigation score.
    """

    scored = calculate_investigation_score(signals)

    ranked = (
        scored
        .sort_values(
            by=[
                "investigation_score",
                "max_payment_award_ratio",
                "duplicate_payment_groups",
            ],
            ascending=False,
        )
        .reset_index(drop=True)
    )

    ranked["rank"] = ranked.index + 1

    if top_n is None:
        return ranked

    return ranked.head(top_n)
