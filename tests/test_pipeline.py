from src.pipeline import run_pipeline


def test_pipeline_runs():

    (
        cases,
        payments,
        features,
        signals,
        ranked_cases,
        final_worklist,
        fairness_results,
        feedback,
    ) = run_pipeline()

    assert len(cases) == 4200
    assert len(payments) == 24756
    assert len(features) == 4200
    assert len(signals) == 4200
    assert len(ranked_cases) == 4200
    assert len(final_worklist) == 20
