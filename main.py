from src.data_loader import load_data, DataValidationError
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import calculate_investigation_score, create_ranked_worklist
from src.explanations import add_explanations
from src.fairness import analyze_fairness
import os

def main():
    print("=" * 60)
    print("BRITE SPARK 2026 — PROBLEM 6")
    print("THE OVERPAYMENT SIGNAL PIPELINE")
    print("=" * 60)

    try:
        # -----------------------------------------------------
        # 1. Load data
        # -----------------------------------------------------
        cases, payments = load_data()

        print("\n✓ Data loading successful.")
        print(f"  Cases loaded:    {len(cases):,}")
        print(f"  Payments loaded: {len(payments):,}")

        # -----------------------------------------------------
        # 2. Feature engineering
        # -----------------------------------------------------
        print("\nCreating payment features...")
        features = create_payment_features(cases, payments)
        print("✓ Feature engineering successful.")

        # -----------------------------------------------------
        # 3. Signal generation
        # -----------------------------------------------------
        print("\nGenerating risk signals...")
        signals = generate_signals(features)
        print("✓ Risk signal generation successful.")

        # -----------------------------------------------------
        # 4. Case ranking
        # -----------------------------------------------------
        print("\nRanking prioritized cases...")
        ranked = create_ranked_worklist(signals, top_n=4200)
        
        # Also print the specific TOP 20 WORKLIST requested by the user
        worklist = create_ranked_worklist(signals, top_n=20)
        worklist = add_explanations(worklist)
        
        print("\n" + "=" * 60)
        print("TOP 20 INVESTIGATION WORKLIST")
        print("=" * 60)
        
        for _, row in worklist.iterrows():
            print(
                f"\nRank {int(row['rank'])}: {row['case_id']}"
            )
            print(
                f"Score: {row['investigation_score']:.3f}"
            )
            print(
                f"Reason: {row['reason']}"
            )
        print("=" * 60)
        print("✓ Case ranking successful.")

        # -----------------------------------------------------
        # 5. Plain-language explanations
        # -----------------------------------------------------
        print("\nGenerating plain-language explanations...")
        explained = add_explanations(ranked)
        print("✓ Explanation generation successful.")

        # -----------------------------------------------------
        # 6. Fairness analysis
        # -----------------------------------------------------
        print("\nPerforming demographic fairness analysis...")
        fairness_report = analyze_fairness(explained, output_dir="output")
        print("✓ Fairness analysis completed (saved to output/fairness_report.csv).")

        # -----------------------------------------------------
        # 7. Write outputs
        # -----------------------------------------------------
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save full worklist
        explained.to_csv(os.path.join(output_dir, "ranked_cases.csv"), index=False)
        
        # Save top 20
        top_20 = explained.head(20).copy()
        top_20_summary = top_20[["rank", "case_id", "investigation_score", "reason", "evidence"]]
        top_20_summary.to_csv(os.path.join(output_dir, "top_20_worklist.csv"), index=False)
        print("✓ Saved ranked worklist and top 20 to output/ directory.")

        # -----------------------------------------------------
        # 8. Print Top 20 table
        # -----------------------------------------------------
        print("\n" + "=" * 90)
        print("TOP 20 RANKED BENEFIT CASES FOR INVESTIGATION REVIEW")
        print("=" * 90)
        print(f"{'Rank':<5} | {'Case ID':<10} | {'Score':<6} | {'Reason'}")
        print("-" * 90)
        for _, row in top_20_summary.iterrows():
            reason = row["reason"]
            # Truncate reason if too long for display
            if len(reason) > 60:
                reason = reason[:57] + "..."
            print(f"{int(row['rank']):<5} | {row['case_id']:<10} | {row['investigation_score']:<6.4f} | {reason}")
        print("=" * 90)

    except FileNotFoundError as error:
        print(f"\nERROR: {error}")

    except DataValidationError as error:
        print(f"\nDATA VALIDATION ERROR: {error}")


if __name__ == "__main__":
    main()