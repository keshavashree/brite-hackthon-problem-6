from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals


def get_signals():
    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments
    )

    return generate_signals(features)


def test_signal_row_count():
    signals = get_signals()

    assert len(signals) == 4200


def test_signal_case_ids_are_unique():
    signals = get_signals()

    assert signals["case_id"].is_unique


def test_c33248_has_no_strong_financial_signals():
    signals = get_signals()

    case = signals[
        signals["case_id"] == "C-33248"
    ].iloc[0]

    # The case has no months where payment exceeds
    # 1.25x, 1.50x, or 2.00x of the recorded award.
    assert case["months_over_1_25"] == 0
    assert case["months_over_1_50"] == 0
    assert case["months_over_2_00"] == 0

    # No duplicate payment pattern was identified.
    assert case["duplicate_payment_groups"] == 0

    # A small payment variation should not itself create
    # a strong award-deviation signal.
    assert case["award_deviation_signal"] == 0