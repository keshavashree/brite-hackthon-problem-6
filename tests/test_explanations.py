from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import create_ranked_worklist
from src.explanations import add_explanations


def get_worklist():
    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments
    )

    signals = generate_signals(features)

    worklist = create_ranked_worklist(
        signals,
        top_n=20
    )

    return add_explanations(worklist, payments=payments)


def test_every_case_has_reason():
    worklist = get_worklist()

    assert worklist["reason"].notna().all()
    assert (worklist["reason"].str.len() > 0).all()


def test_every_case_has_evidence():
    worklist = get_worklist()

    assert worklist["evidence"].notna().all()
    assert (worklist["evidence"].str.len() > 0).all()


def test_every_case_has_detailed_evidence():
    worklist = get_worklist()

    assert "detailed_evidence" in worklist.columns
    assert worklist["detailed_evidence"].notna().all()
    assert (worklist["detailed_evidence"].str.len() > 0).all()


def test_worklist_still_contains_20_cases():
    worklist = get_worklist()

    assert len(worklist) == 20
