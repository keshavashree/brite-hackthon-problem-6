from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import create_ranked_worklist
from src.explanations import generate_explanations

def get_explained_data():
    cases, payments = load_data()
    features = create_payment_features(cases, payments)
    signals = generate_signals(features)
    ranked = create_ranked_worklist(signals, top_n=4200)
    return generate_explanations(ranked)

def test_explanations_exist():
    explained = get_explained_data()
    assert "explanation" in explained.columns
    assert explained["explanation"].isna().sum() == 0

def test_c33248_explanation():
    explained = get_explained_data()
    c33248 = explained[explained["case_id"] == "C-33248"].iloc[0]
    
    assert c33248["explanation"] == "No strong payment anomalies or risk signals were identified."

def test_top_cases_explanations():
    explained = get_explained_data()
    # Check that top 5 cases have actual reasons (they should not have the default "No strong payment anomalies...")
    top_5 = explained.head(5)
    for idx, row in top_5.iterrows():
        assert "Flagged because" in row["explanation"]
