import pandas as pd


def build_fairness_summary(
    fairness_results: dict[int, dict[str, pd.DataFrame]]
) -> pd.DataFrame:
    """
    Combine fairness audit results from multiple ranking cutoffs
    into one report.
    """

    rows = []

    for k, reports in fairness_results.items():

        for dimension, report in reports.items():

            for _, row in report.iterrows():

                rows.append(
                    {
                        "cutoff": k,
                        "dimension": dimension,
                        "group": row[dimension],
                        "population_count": row["population_count"],
                        "population_rate": row["population_rate"],
                        "selected_count": row["selected_count"],
                        "selected_rate": row["selected_rate"],
                        "selection_ratio": row["selection_ratio"],
                    }
                )

    return pd.DataFrame(rows)


def classify_selection_ratio(
    ratio: float
) -> str:
    """
    Provide a simple governance interpretation.

    This is descriptive, not a statistical fairness determination.
    """

    if pd.isna(ratio):
        return "Insufficient data"

    if ratio < 0.80:
        return "Below population share"

    if ratio > 1.25:
        return "Above population share"

    return "Close to population share"


def add_interpretation(
    summary: pd.DataFrame
) -> pd.DataFrame:

    result = summary.copy()

    result["interpretation"] = (
        result["selection_ratio"]
        .apply(classify_selection_ratio)
    )

    return result
