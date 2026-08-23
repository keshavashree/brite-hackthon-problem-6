from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import (
    calculate_investigation_score,
    create_ranked_worklist,
)


def get_signals():
    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments
    )

    return generate_signals(features)


def test_scores_are_created():
    signals = get_signals()

    scored = calculate_investigation_score(signals)

    assert "investigation_score" in scored.columns
    assert len(scored) == 4200


def test_scores_are_non_negative():
    signals = get_signals()

    scored = calculate_investigation_score(signals)

    assert (scored["investigation_score"] >= 0).all()


def test_worklist_contains_20_cases():
    signals = get_signals()

    worklist = create_ranked_worklist(
        signals,
        top_n=20
    )

    assert len(worklist) == 20


def test_worklist_ranks_are_correct():
    signals = get_signals()

    worklist = create_ranked_worklist(
        signals,
        top_n=20
    )

    assert list(worklist["rank"]) == list(range(1, 21))


def test_worklist_case_ids_are_unique():
    signals = get_signals()

    worklist = create_ranked_worklist(
        signals,
        top_n=20
    )

    assert worklist["case_id"].is_unique


def test_c33248_not_selected_due_to_strong_financial_signals():
    signals = get_signals()

    worklist = create_ranked_worklist(
        signals,
        top_n=20
    )

    assert "C-33248" not in set(worklist["case_id"])
