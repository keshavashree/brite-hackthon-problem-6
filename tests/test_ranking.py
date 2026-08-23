from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import calculate_rankings

def get_ranked_data():
    cases, payments = load_data()
    features = create_payment_features(cases, payments)
    signals = generate_signals(features)
    return calculate_rankings(signals)

def test_ranking_row_count():
    ranked = get_ranked_data()
    assert len(ranked) == 4200

def test_ranking_scores_bounded():
    ranked = get_ranked_data()
    assert ranked["prioritisation_score"].min() >= 0.0
    assert ranked["prioritisation_score"].max() <= 1.0

def test_ranking_sequential():
    ranked = get_ranked_data()
    expected_ranks = list(range(1, 4201))
    assert list(ranked["rank"]) == expected_ranks

def test_c33248_not_in_top_20():
    ranked = get_ranked_data()
    top_20_case_ids = set(ranked.head(20)["case_id"])
    assert "C-33248" not in top_20_case_ids
