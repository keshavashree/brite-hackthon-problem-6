import pandas as pd

from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import create_ranked_worklist
from src.feedback import apply_feedback


def main():

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

    # Artificial investigator feedback for demonstration.
    #
    # This is NOT a real finding. It only tests whether the
    # architecture can change the treatment of a signal category.

    feedback = pd.DataFrame(
        {
            "case_id": ["C-31298"],
            "feedback_type": ["false_positive"],
            "reason": [
                "Controlled test: payment deviation was determined "
                "to be legitimate."
            ],
            "signal_category": [
                "payment_deviation"
            ],
            "action": [
                "downweight"
            ],
        }
    )

    updated = apply_feedback(
        ranked,
        feedback,
    )

    before = ranked[
        ranked["case_id"] == "C-31298"
    ].iloc[0]

    after = updated[
        updated["case_id"] == "C-31298"
    ].iloc[0]

    print("\nCONTROLLED FEEDBACK TEST")
    print("-" * 60)

    print(
        f"Case: {before['case_id']}"
    )

    print(
        f"Original score: "
        f"{before['investigation_score']:.4f}"
    )

    print(
        f"Updated score:  "
        f"{after['adjusted_score']:.4f}"
    )

    print(
        f"Score change:   "
        f"{after['adjusted_score'] - before['investigation_score']:.4f}"
    )

    print(
        f"Original rank:  "
        f"{int(before['rank'])}"
    )

    print(
        f"Updated rank:   "
        f"{int(after['rank_after_feedback'])}"
    )


if __name__ == "__main__":
    main()
