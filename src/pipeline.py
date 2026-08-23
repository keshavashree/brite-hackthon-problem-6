from pathlib import Path

from src.data_loader import load_data
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import create_ranked_worklist
from src.explanations import add_explanations
from src.fairness import run_fairness_audit_at_k
from src.feedback import load_feedback, apply_feedback
from src.fairness_report import build_fairness_summary, add_interpretation


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"


def run_pipeline():
    """
    Execute the complete Problem 6 pipeline.

    Returns:
        cases
        payments
        features
        signals
        ranked_after_feedback
        final_worklist
        fairness_results
        feedback
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # 1. Load and validate source data
    # ---------------------------------------------------------
    cases, payments = load_data()

    # ---------------------------------------------------------
    # 2. Feature engineering
    # ---------------------------------------------------------
    features = create_payment_features(
        cases,
        payments,
    )

    # ---------------------------------------------------------
    # 3. Generate investigation signals
    # ---------------------------------------------------------
    signals = generate_signals(
        features,
    )

    # ---------------------------------------------------------
    # 4. Create complete base ranking
    # ---------------------------------------------------------
    ranked_cases = create_ranked_worklist(
        signals,
        top_n=None,
    )

    # ---------------------------------------------------------
    # 5. Load investigator feedback
    # ---------------------------------------------------------
    feedback = load_feedback()

    # ---------------------------------------------------------
    # 6. Apply feedback without retraining
    # ---------------------------------------------------------
    ranked_after_feedback = apply_feedback(
        ranked_cases,
        feedback,
    )

    feedback_comparison = ranked_cases[
        [
            "case_id",
            "investigation_score",
        ]
    ].copy()

    feedback_comparison = feedback_comparison.merge(
        ranked_after_feedback[
            [
                "case_id",
                "adjusted_score",
                "rank_after_feedback",
            ]
        ],
        on="case_id",
        how="left",
    )

    feedback_comparison["score_change"] = (
        feedback_comparison["adjusted_score"]
        - feedback_comparison["investigation_score"]
    )

    feedback_comparison.to_csv(
        OUTPUT_DIR / "feedback_comparison.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # 7. Final Top 20
    # ---------------------------------------------------------
    final_worklist = ranked_after_feedback.head(20)

    final_worklist = add_explanations(
        final_worklist,
        payments=payments,
    )

    # ---------------------------------------------------------
    # 8. Fairness audit
    # ---------------------------------------------------------
    fairness_results = run_fairness_audit_at_k(
        cases,
        ranked_after_feedback,
        k_values=[20, 50, 100, 200],
    )

    fairness_summary = build_fairness_summary(
        fairness_results
    )

    fairness_summary = add_interpretation(
        fairness_summary
    )

    fairness_summary.to_csv(
        OUTPUT_DIR / "fairness_summary.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # 9. Save ranked outputs
    # ---------------------------------------------------------

    ranked_after_feedback.to_csv(
        OUTPUT_DIR / "ranked_cases.csv",
        index=False,
    )

    final_worklist.to_csv(
        OUTPUT_DIR / "worklist.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # 10. Save fairness reports
    # ---------------------------------------------------------

    for k, reports in fairness_results.items():

        for dimension, report in reports.items():

            filename = (
                f"fairness_top{k}_{dimension}.csv"
            )

            report.to_csv(
                OUTPUT_DIR / filename,
                index=False,
            )

    summary_file = OUTPUT_DIR / "run_summary.txt"

    with open(
        summary_file,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "BRITE SPARK 2026 — PROBLEM 6\n"
        )

        file.write(
            "THE OVERPAYMENT SIGNAL\n\n"
        )

        file.write(
            f"Cases: {len(cases):,}\n"
        )

        file.write(
            f"Payments: {len(payments):,}\n"
        )

        file.write(
            f"Ranked cases: {len(ranked_after_feedback):,}\n"
        )

        file.write(
            f"Feedback records: {len(feedback):,}\n"
        )

        file.write(
            f"Final worklist size: {len(final_worklist):,}\n"
        )

    return (
        cases,
        payments,
        features,
        signals,
        ranked_after_feedback,
        final_worklist,
        fairness_results,
        feedback,
    )
