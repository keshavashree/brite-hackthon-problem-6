from src.pipeline import run_pipeline


def main():
    print("=" * 65)
    print("BRITE SPARK 2026 — PROBLEM 6")
    print("THE OVERPAYMENT SIGNAL")
    print("=" * 65)

    try:
        (
            cases,
            payments,
            features,
            signals,
            ranked_cases,
            final_worklist,
            fairness_results,
            feedback,
        ) = run_pipeline()

        print("\n✓ Pipeline completed successfully.")

        print(f"\nCases:             {len(cases):,}")
        print(f"Payments:          {len(payments):,}")
        print(f"Feature rows:      {len(features):,}")
        print(f"Ranked cases:      {len(ranked_cases):,}")
        print(f"Feedback records:  {len(feedback):,}")
        print(f"Final worklist:    {len(final_worklist):,}")

        print("\n" + "-" * 65)
        print("TOP 20 INVESTIGATION WORKLIST")
        print("-" * 65)

        for _, row in final_worklist.iterrows():
            print(
                f"\n#{int(row['rank_after_feedback']):02d} "
                f"{row['case_id']}"
            )

            print(
                f"Score:  {row['adjusted_score']:.3f}"
            )

            print(
                f"Reason: {row['reason']}"
            )

            print(
                f"Evidence: {row['evidence']}"
            )

            if "detailed_evidence" in row and row["detailed_evidence"]:
                print("Monthly Details:")
                for month_detail in row["detailed_evidence"].split(" | "):
                    print(f"  - {month_detail}")

        print("\n" + "=" * 65)
        print("Pipeline finished.")
        print("=" * 65)

    except Exception as error:
        print(
            f"\nPIPELINE ERROR: {error}"
        )
        raise


if __name__ == "__main__":
    main()