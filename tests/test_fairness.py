from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import create_ranked_worklist
from src.fairness import run_fairness_audit


def get_data():

    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments,
    )

    signals = generate_signals(
        features,
    )

    ranked = create_ranked_worklist(
        signals,
        top_n=None,
    )

    return cases, ranked


def test_required_fairness_dimensions():

    cases, ranked = get_data()

    worklist = ranked.head(20)

    results = run_fairness_audit(
        cases,
        worklist,
    )

    assert set(results.keys()) == {
        "age_band",
        "language_preference",
        "district",
        "tenure",
    }


def test_fairness_reports_contain_selection_ratio():

    cases, ranked = get_data()

    worklist = ranked.head(20)

    results = run_fairness_audit(
        cases,
        worklist,
    )

    for report in results.values():

        assert "population_rate" in report.columns
        assert "selected_rate" in report.columns
        assert "selection_ratio" in report.columns
