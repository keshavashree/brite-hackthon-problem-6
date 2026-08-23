import os
from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import calculate_rankings
from src.fairness import analyze_fairness

def get_fairness_data():
    cases, payments = load_data()
    features = create_payment_features(cases, payments)
    signals = generate_signals(features)
    ranked = calculate_rankings(signals)
    return analyze_fairness(ranked, output_dir="output_temp")

def test_fairness_columns():
    report = get_fairness_data()
    expected_cols = {
        "demographic_dimension",
        "group_value",
        "population_count",
        "population_share",
        "top_20_count",
        "top_20_selection_rate",
        "top_100_count",
        "top_100_selection_rate"
    }
    assert expected_cols.issubset(report.columns)

def test_fairness_totals():
    report = get_fairness_data()
    
    # For each dimension, top_20_count should sum to 20
    for dim in ["language_preference", "age_band", "district"]:
        dim_rows = report[report["demographic_dimension"] == dim]
        assert dim_rows["top_20_count"].sum() == 20
        assert dim_rows["top_100_count"].sum() == 100

def test_fairness_file_created():
    if os.path.exists("output_temp/fairness_report.csv"):
        os.remove("output_temp/fairness_report.csv")
    
    _ = get_fairness_data()
    assert os.path.exists("output_temp/fairness_report.csv")
    
    # Clean up temp test files
    if os.path.exists("output_temp/fairness_report.csv"):
        os.remove("output_temp/fairness_report.csv")
    if os.path.exists("output_temp"):
        os.rmdir("output_temp")
