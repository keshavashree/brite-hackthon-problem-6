import pandas as pd


AUDIT_COLUMNS = [
    "age_band",
    "language_preference",
    "district",
    "tenure",
]


def calculate_group_metrics(
    cases: pd.DataFrame,
    ranked_cases: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    """
    Compare population representation with representation
    in the selected investigation worklist.
    """

    population = (
        cases[column]
        .value_counts(dropna=False)
        .rename("population_count")
        .reset_index()
    )

    population.columns = [
        column,
        "population_count",
    ]

    population["population_rate"] = (
        population["population_count"]
        / len(cases)
    )

    selected = (
        ranked_cases[column]
        .value_counts(dropna=False)
        .rename("selected_count")
        .reset_index()
    )

    selected.columns = [
        column,
        "selected_count",
    ]

    result = population.merge(
        selected,
        on=column,
        how="left",
    )

    result["selected_count"] = (
        result["selected_count"]
        .fillna(0)
        .astype(int)
    )

    total_selected = len(ranked_cases)

    if total_selected > 0:
        result["selected_rate"] = (
            result["selected_count"]
            / total_selected
        )
    else:
        result["selected_rate"] = 0.0

    result["selection_ratio"] = (
        result["selected_rate"]
        / result["population_rate"]
    )

    return result


def run_fairness_audit(
    cases: pd.DataFrame,
    worklist: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Run fairness analysis across the required population groups.

    The audit does not modify ranking scores.
    """

    # Add demographic/context columns to the worklist.
    worklist_with_context = worklist.merge(
        cases[
            [
                "case_id",
                "age_band",
                "language_preference",
                "district",
                "tenure",
            ]
        ],
        on="case_id",
        how="left",
    )

    results = {}

    for column in AUDIT_COLUMNS:
        results[column] = calculate_group_metrics(
            cases,
            worklist_with_context,
            column,
        )

    return results


def run_fairness_audit_at_k(
    cases: pd.DataFrame,
    ranked_cases: pd.DataFrame,
    k_values: list[int] | None = None,
) -> dict[int, dict[str, pd.DataFrame]]:
    """
    Run fairness analysis at several ranking cutoffs.
    """

    if k_values is None:
        k_values = [20, 50, 100, 200]

    results = {}

    for k in k_values:

        selected = ranked_cases.head(k)

        results[k] = run_fairness_audit(
            cases,
            selected,
        )

    return results
