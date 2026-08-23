import pandas as pd


def build_reason(row: pd.Series) -> str:
    """
    Generate a plain-language investigation reason
    based on the strongest available financial signals.

    This does not claim that the payment is improper.
    """

    reasons = []

    # ---------------------------------------------------------
    # 1. Persistent severe payment deviation
    # ---------------------------------------------------------
    if row["months_over_2_00"] >= 2:
        reasons.append(
            f"Payments exceeded twice the recorded monthly award "
            f"in {int(row['months_over_2_00'])} months."
        )

    # ---------------------------------------------------------
    # 2. Persistent strong deviation
    # ---------------------------------------------------------
    elif row["months_over_1_50"] >= 2:
        reasons.append(
            f"Payments exceeded 1.5 times the recorded monthly "
            f"award in {int(row['months_over_1_50'])} months."
        )

    # ---------------------------------------------------------
    # 3. Persistent moderate deviation
    # ---------------------------------------------------------
    elif row["months_over_1_25"] >= 3:
        reasons.append(
            f"Payments exceeded 1.25 times the recorded monthly "
            f"award in {int(row['months_over_1_25'])} months."
        )

    # ---------------------------------------------------------
    # 4. Multiple payment months
    # ---------------------------------------------------------
    if row["multiple_payment_months"] > 0:
        reasons.append(
            f"Multiple payments were recorded in "
            f"{int(row['multiple_payment_months'])} month(s)."
        )

    # ---------------------------------------------------------
    # 5. Duplicate payment patterns
    # ---------------------------------------------------------
    if row["duplicate_payment_groups"] > 0:
        reasons.append(
            f"{int(row['duplicate_payment_groups'])} exact "
            f"duplicate payment pattern(s) were identified."
        )

    # ---------------------------------------------------------
    # 6. Large payment change
    # ---------------------------------------------------------
    if row["monthly_award"] > 0:
        change_ratio = (
            row["max_monthly_change"]
            / row["monthly_award"]
        )

        if change_ratio >= 1.00:
            reasons.append(
                "A month-to-month payment change was at least "
                "as large as the recorded monthly award."
            )

    # ---------------------------------------------------------
    # 7. Fallback
    # ---------------------------------------------------------
    if not reasons:
        reasons.append(
            "The case shows a combination of payment patterns "
            "that places it above other cases in the review ranking."
        )

    return " ".join(reasons)


def build_evidence(row: pd.Series) -> str:
    """
    Build a concise evidence summary for an investigator.
    """

    evidence = []

    evidence.append(
        f"Recorded monthly award: "
        f"${row['monthly_award']:,.2f}"
    )

    evidence.append(
        f"Maximum payment/award ratio: "
        f"{row['max_payment_award_ratio']:.2f}x"
    )

    evidence.append(
        f"Months above 1.25x award: "
        f"{int(row['months_over_1_25'])}"
    )

    evidence.append(
        f"Months above 1.50x award: "
        f"{int(row['months_over_1_50'])}"
    )

    evidence.append(
        f"Months above 2.00x award: "
        f"{int(row['months_over_2_00'])}"
    )

    evidence.append(
        f"Multiple-payment months: "
        f"{int(row['multiple_payment_months'])}"
    )

    evidence.append(
        f"Duplicate-payment groups: "
        f"{int(row['duplicate_payment_groups'])}"
    )

    return " | ".join(evidence)


def add_explanations(worklist: pd.DataFrame) -> pd.DataFrame:
    """
    Add plain-language reasons and supporting evidence.
    """

    result = worklist.copy()

    result["reason"] = result.apply(
        build_reason,
        axis=1
    )

    result["evidence"] = result.apply(
        build_evidence,
        axis=1
    )

    return result
