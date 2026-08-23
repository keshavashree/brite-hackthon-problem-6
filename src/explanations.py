import pandas as pd

def explain_case(row: pd.Series) -> str:
    """
    Generate a non-technical, plain-language explanation of flags in a case.
    """
    reasons = []
    
    # 1. Extreme deviation
    if row.get("extreme_deviation_signal", 0.0) > 0:
        months_over_2 = int(row.get("months_over_2_00", 0))
        reasons.append(f"monthly payments exceeded 2.0x of the recorded award in {months_over_2} month(s)")
        
    # 2. Duplicate payments
    if row.get("duplicate_payment_groups", 0.0) > 0:
        groups = int(row.get("duplicate_payment_groups", 0))
        reasons.append(f"duplicate payment patterns identified ({groups} group(s) of identical payment amounts within the same month)")
        
    # 3. High award deviation
    if row.get("award_deviation_signal", 0.0) > 0:
        max_ratio = row.get("max_payment_award_ratio", 1.0)
        reasons.append(f"maximum monthly payment was {max_ratio:.2f}x of the recorded award")
        
    # 4. Persistent deviation (excluding case when extreme is already mentioned or keep it simple)
    if row.get("persistence_signal", 0.0) > 0:
        months_over_1_25 = int(row.get("months_over_1_25", 0))
        reasons.append(f"payments exceeded 1.25x of the award in {months_over_1_25} month(s)")
        
    # 5. Volatility
    if row.get("monthly_change_signal", 0.0) > 1.0:
        change_ratio = row.get("monthly_change_signal", 0.0)
        reasons.append(f"monthly payments showed high volatility (largest change was {change_ratio:.2f}x of the award)")
        
    # 6. Multiple payments
    if row.get("multiple_payment_signal", 0.0) > 0:
        multiple_months = int(row.get("multiple_payment_months", 0))
        reasons.append(f"multiple distinct payments were issued in {multiple_months} month(s)")

    # Combine
    if not reasons:
        return "No strong payment anomalies or risk signals were identified."
    elif len(reasons) == 1:
        return f"Flagged because {reasons[0]}."
    else:
        # Capitalize the first letter of first reason and join
        return "Flagged because: " + "; ".join(reasons) + "."


def generate_explanations(ranked_cases: pd.DataFrame) -> pd.DataFrame:
    """
    Append plain-language explanations to the ranked benefits worklist.
    """
    df = ranked_cases.copy()
    df["explanation"] = df.apply(explain_case, axis=1)
    return df
