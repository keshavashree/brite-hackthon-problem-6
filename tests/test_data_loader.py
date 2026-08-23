from src.data_loader import load_data


def test_load_data():
    cases, payments = load_data()

    assert len(cases) == 4200
    assert len(payments) == 24756


def test_case_ids_are_unique():
    cases, _ = load_data()

    assert cases["case_id"].is_unique


def test_payment_ids_are_unique():
    _, payments = load_data()

    assert payments["payment_id"].is_unique


def test_all_payments_reference_known_cases():
    cases, payments = load_data()

    known_cases = set(cases["case_id"])

    assert set(payments["case_id"]).issubset(known_cases)