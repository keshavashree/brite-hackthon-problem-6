import pandas as pd
import numpy as np


def create_payment_features(
    cases: pd.DataFrame,
    payments: pd.DataFrame
) -> pd.DataFrame:
    """
    Create one feature row per case.

    These features describe payment behaviour only.
    Demographic fields are intentionally not used to calculate
    the initial financial risk signals.
    """

    # ---------------------------------------------------------
    # 1. Convert payment month to datetime
    # ---------------------------------------------------------
    payments = payments.copy()
    payments["pay_month"] = pd.to_datetime(
        payments["pay_month"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 2. Basic payment-level features
    # ---------------------------------------------------------
    payment_summary = (
        payments
        .groupby("case_id")
        .agg(
            payment_count=("payment_id", "count"),
            total_paid=("amount", "sum"),
            mean_payment=("amount", "mean"),
            median_payment=("amount", "median"),
            max_payment=("amount", "max"),
            min_payment=("amount", "min"),
            payment_std=("amount", "std"),
            payment_months=("pay_month", "nunique"),
        )
        .reset_index()
    )

    payment_summary["payment_std"] = (
        payment_summary["payment_std"].fillna(0)
    )

    # ---------------------------------------------------------
    # 3. Monthly payment totals
    # ---------------------------------------------------------
    monthly = (
        payments
        .groupby(["case_id", "pay_month"], as_index=False)
        .agg(
            monthly_payment=("amount", "sum"),
            payments_in_month=("payment_id", "count"),
        )
    )

    # ---------------------------------------------------------
    # 4. Attach monthly award
    # ---------------------------------------------------------
    monthly = monthly.merge(
        cases[["case_id", "monthly_award"]],
        on="case_id",
        how="left"
    )

    # Avoid division by zero
    monthly["payment_award_ratio"] = np.where(
        monthly["monthly_award"] > 0,
        monthly["monthly_payment"] / monthly["monthly_award"],
        np.nan
    )

    # ---------------------------------------------------------
    # 5. Payment / award ratio features
    # ---------------------------------------------------------
    ratio_features = (
        monthly
        .groupby("case_id")
        .agg(
            mean_payment_award_ratio=(
                "payment_award_ratio",
                "mean"
            ),
            max_payment_award_ratio=(
                "payment_award_ratio",
                "max"
            ),
            min_payment_award_ratio=(
                "payment_award_ratio",
                "min"
            ),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # 6. Count months above important thresholds
    # ---------------------------------------------------------
    threshold_features = (
        monthly
        .groupby("case_id")
        .agg(
            months_over_award=(
                "payment_award_ratio",
                lambda x: (x > 1.0).sum()
            ),
            months_over_1_25=(
                "payment_award_ratio",
                lambda x: (x >= 1.25).sum()
            ),
            months_over_1_50=(
                "payment_award_ratio",
                lambda x: (x >= 1.50).sum()
            ),
            months_over_2_00=(
                "payment_award_ratio",
                lambda x: (x >= 2.00).sum()
            ),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # 7. Multiple-payment months
    # ---------------------------------------------------------
    multiple_payment_features = (
        monthly
        .groupby("case_id")
        .agg(
            multiple_payment_months=(
                "payments_in_month",
                lambda x: (x > 1).sum()
            ),
            max_payments_in_month=(
                "payments_in_month",
                "max"
            ),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # 8. Exact duplicate payment patterns
    #
    # Same case + same month + same amount
    # ---------------------------------------------------------
    duplicate_groups = (
        payments
        .groupby(["case_id", "pay_month", "amount"])
        .size()
        .reset_index(name="duplicate_count")
    )

    duplicate_features = (
        duplicate_groups
        .groupby("case_id")
        .agg(
            duplicate_payment_groups=(
                "duplicate_count",
                lambda x: (x > 1).sum()
            ),
            duplicate_payment_records=(
                "duplicate_count",
                lambda x: (x[x > 1] - 1).sum()
            ),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # 9. Month-to-month payment changes
    # ---------------------------------------------------------
    monthly = monthly.sort_values(
        ["case_id", "pay_month"]
    )

    monthly["previous_month_payment"] = (
        monthly
        .groupby("case_id")["monthly_payment"]
        .shift(1)
    )

    monthly["absolute_monthly_change"] = (
        monthly["monthly_payment"]
        - monthly["previous_month_payment"]
    ).abs()

    change_features = (
        monthly
        .groupby("case_id")
        .agg(
            max_monthly_change=(
                "absolute_monthly_change",
                "max"
            ),
            mean_monthly_change=(
                "absolute_monthly_change",
                "mean"
            ),
        )
        .reset_index()
    )

    change_features[
        ["max_monthly_change", "mean_monthly_change"]
    ] = change_features[
        ["max_monthly_change", "mean_monthly_change"]
    ].fillna(0)

    # ---------------------------------------------------------
    # 10. Combine all features
    # ---------------------------------------------------------
    features = cases[
        [
            "case_id",
            "monthly_award",
            "household_size",
            "payment_adjustments",
            "contact_attempts",
            "months_since_review",
        ]
    ].copy()

    features = features.merge(
        payment_summary,
        on="case_id",
        how="left"
    )

    features = features.merge(
        ratio_features,
        on="case_id",
        how="left"
    )

    features = features.merge(
        threshold_features,
        on="case_id",
        how="left"
    )

    features = features.merge(
        multiple_payment_features,
        on="case_id",
        how="left"
    )

    features = features.merge(
        duplicate_features,
        on="case_id",
        how="left"
    )

    features = features.merge(
        change_features,
        on="case_id",
        how="left"
    )

    # ---------------------------------------------------------
    # 11. Fill features that can legitimately be zero
    # ---------------------------------------------------------
    zero_fill_columns = [
        "payment_count",
        "total_paid",
        "mean_payment",
        "median_payment",
        "max_payment",
        "min_payment",
        "payment_std",
        "payment_months",
        "months_over_award",
        "months_over_1_25",
        "months_over_1_50",
        "months_over_2_00",
        "multiple_payment_months",
        "max_payments_in_month",
        "duplicate_payment_groups",
        "duplicate_payment_records",
        "max_monthly_change",
        "mean_monthly_change",
    ]

    for column in zero_fill_columns:
        if column in features.columns:
            features[column] = features[column].fillna(0)

    return features