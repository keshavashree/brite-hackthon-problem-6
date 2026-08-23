import pandas as pd

from src.fairness_report import (
    classify_selection_ratio,
    build_fairness_summary,
)


def test_ratio_classification():

    assert (
        classify_selection_ratio(0.70)
        == "Below population share"
    )

    assert (
        classify_selection_ratio(1.00)
        == "Close to population share"
    )

    assert (
        classify_selection_ratio(1.50)
        == "Above population share"
    )


def test_fairness_summary_structure():

    report = pd.DataFrame(
        {
            "age_band": ["30-44"],
            "population_count": [100],
            "population_rate": [0.50],
            "selected_count": [10],
            "selected_rate": [0.50],
            "selection_ratio": [1.00],
        }
    )

    results = {
        20: {
            "age_band": report
        }
    }

    summary = build_fairness_summary(
        results
    )

    assert len(summary) == 1
    assert summary.iloc[0]["cutoff"] == 20
    assert summary.iloc[0]["dimension"] == "age_band"
