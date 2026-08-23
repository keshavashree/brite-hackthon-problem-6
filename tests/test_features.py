from src.data_loader import load_data
from src.feature_engineering import create_payment_features


def test_feature_row_count():
    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments
    )

    assert len(features) == 4200


def test_case_ids_are_unique():
    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments
    )

    assert features["case_id"].is_unique


def test_c33248_financial_signals():
    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments
    )

    case = features[
        features["case_id"] == "C-33248"
    ].iloc[0]

    assert case["months_over_1_25"] == 0
    assert case["months_over_1_50"] == 0
    assert case["months_over_2_00"] == 0
    assert case["duplicate_payment_groups"] == 0