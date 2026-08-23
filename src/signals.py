import pandas as pd
import numpy as np


def generate_signals(features: pd.DataFrame) -> pd.DataFrame:
    """
    Convert engineered case-level features into explainable
    investigation signals.

    These signals do not establish improper payment.
    They identify patterns that may warrant human review.
    """

    signals = features.copy()

    # ---------------------------------------------------------
    # 1. Payment / award deviation
    # ---------------------------------------------------------
    signals["award_deviation_signal"] = np.select(
        [
            signals["max_payment_award_ratio"] >= 2.00,
            signals["max_payment_award_ratio"] >= 1.50,
            signals["max_payment_award_ratio"] >= 1.25,
            signals["max_payment_award_ratio"] >= 1.10,
        ],
        [
            1.00,
            0.75,
            0.50,
            0.25,
        ],
        default=0.0,
    )

    # ---------------------------------------------------------
    # 2. Persistent deviation
    # ---------------------------------------------------------
    signals["persistence_signal"] = (
        signals["months_over_1_25"] / signals["payment_months"].clip(lower=1)
    )

    # ---------------------------------------------------------
    # 3. Strong persistent deviation
    # ---------------------------------------------------------
    signals["severe_persistence_signal"] = (
        signals["months_over_1_50"] / signals["payment_months"].clip(lower=1)
    )

    # ---------------------------------------------------------
    # 4. Extreme payment deviation
    # ---------------------------------------------------------
    signals["extreme_deviation_signal"] = (
        signals["months_over_2_00"] / signals["payment_months"].clip(lower=1)
    )

    # ---------------------------------------------------------
    # 5. Multiple-payment signal
    # ---------------------------------------------------------
    signals["multiple_payment_signal"] = (
        signals["multiple_payment_months"]
        / signals["payment_months"].clip(lower=1)
    )

    # ---------------------------------------------------------
    # 6. Duplicate-payment signal
    # ---------------------------------------------------------
    signals["duplicate_payment_signal"] = (
        signals["duplicate_payment_groups"]
        / signals["payment_months"].clip(lower=1)
    )

    # ---------------------------------------------------------
    # 7. Payment volatility
    #
    # Compare maximum monthly change with recorded award.
    # ---------------------------------------------------------
    signals["monthly_change_signal"] = np.where(
        signals["monthly_award"] > 0,
        signals["max_monthly_change"]
        / signals["monthly_award"],
        0,
    )

    # ---------------------------------------------------------
    # 8. Administrative activity is deliberately NOT included
    # in the financial investigation score.
    #
    # These are retained for governance/fairness analysis:
    #
    # - payment_adjustments
    # - contact_attempts
    #
    # The Surprise Challenge demonstrated that these can represent
    # Department activity rather than resident-related risk.
    # ---------------------------------------------------------

    return signals