import pandas as pd

from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import create_ranked_worklist
from src.feedback import load_feedback, apply_feedback


def main():

    print("=" * 70)
    print("BRITE SPARK 2026 — SURPRISE CHALLENGE DEMO")
    print("=" * 70)

    # ---------------------------------------------------------
    # STEP 1 — Build original ranking
    # ---------------------------------------------------------

    cases, payments = load_data()

    features = create_payment_features(
        cases,
        payments,
    )

    signals = generate_signals(
        features,
    )

    base_ranking = create_ranked_worklist(
        signals,
        top_n=None,
    )

    # ---------------------------------------------------------
    # STEP 2 — Load investigator feedback
    # ---------------------------------------------------------

    feedback = load_feedback()

    # ---------------------------------------------------------
    # STEP 3 — Apply feedback
    # ---------------------------------------------------------

    updated_ranking = apply_feedback(
        base_ranking,
        feedback,
    )

    # ---------------------------------------------------------
    # STEP 4 — Compare
    # ---------------------------------------------------------

    comparison = base_ranking[
        [
            "case_id",
            "investigation_score",
        ]
    ].merge(
        updated_ranking[
            [
                "case_id",
                "adjusted_score",
                "rank_after_feedback",
            ]
        ],
        on="case_id",
    )

    comparison["score_change"] = (
        comparison["adjusted_score"]
        - comparison["investigation_score"]
    )

    comparison["rank_change"] = (
        comparison["rank_after_feedback"]
        - comparison.index
        - 1
    )

    # ---------------------------------------------------------
    # STEP 5 — Show feedback
    # ---------------------------------------------------------

    print("\nINVESTIGATOR FEEDBACK")
    print("-" * 70)

    if feedback.empty:
        print("No investigator feedback supplied.")
    else:
        print(
            feedback[
                [
                    "case_id",
                    "feedback_type",
                    "signal_category",
                    "action",
                    "reason",
                ]
            ].to_string(index=False)
        )

    # ---------------------------------------------------------
    # STEP 6 — Show affected cases
    # ---------------------------------------------------------

    if not feedback.empty:

        affected_ids = set(
            feedback["case_id"]
        )

        affected = comparison[
            comparison["case_id"].isin(
                affected_ids
            )
        ]

        print("\nAFFECTED CASES")
        print("-" * 70)

        print(
            affected.to_string(
                index=False
            )
        )

    # ---------------------------------------------------------
    # STEP 7 — Final Top 20
    # ---------------------------------------------------------

    print("\nFINAL TOP 20")
    print("-" * 70)

    print(
        updated_ranking[
            [
                "rank_after_feedback",
                "case_id",
                "investigation_score",
                "adjusted_score",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("SURPRISE CHALLENGE COMPLETE")
    print("=" * 70)

    print(
        "\nThe ranking was updated using investigator feedback "
        "without retraining a machine-learning model."
    )


if __name__ == "__main__":
    main()
