from src.data_loader import load_data, DataValidationError
from src.feature_engineering import create_payment_features
from src.signals import generate_signals
from src.ranking import calculate_investigation_score, create_ranked_worklist
from src.explanations import add_explanations
from src.fairness import run_fairness_audit_at_k
import pandas as pd
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
        ranked_cases = create_ranked_worklist(signals, top_n=None)
        worklist = ranked_cases.head(20)
        print("✓ Case ranking successful.")

        # -----------------------------------------------------
        # 5. Plain-language explanations
        # -----------------------------------------------------
        print("\nGenerating plain-language explanations...")
        worklist = add_explanations(worklist)
        explained_all = add_explanations(ranked_cases)
        print("✓ Explanation generation successful.")

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

        # -----------------------------------------------------
        # 6. Fairness analysis
        # -----------------------------------------------------
        print("\nPerforming demographic fairness analysis...")
        fairness_results = run_fairness_audit_at_k(cases, ranked_cases)
        
        print("\n" + "=" * 60)
        print("FAIRNESS AUDIT")
        print("=" * 60)

        # Display audit reports
        for k, results in fairness_results.items():
            print(f"\n=================== Cutoff k = {k} ===================")
            for dimension, report in results.items():
                print(f"\n--- {dimension} ---")
                print(report.to_string(index=False))
        print("=" * 60)
        print("✓ Fairness analysis completed.")

        # -----------------------------------------------------
        # 7. Write outputs
        # -----------------------------------------------------
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save full worklist
        explained_all.to_csv(os.path.join(output_dir, "ranked_cases.csv"), index=False)
        
        # Save top 20
        top_20 = worklist.copy()
        top_20_summary = top_20[["rank", "case_id", "investigation_score", "reason", "evidence"]]
        top_20_summary.to_csv(os.path.join(output_dir, "top_20_worklist.csv"), index=False)
        
        # Save fairness reports
        # Save the k=20 report to output/fairness_report.csv
        k_20_reports = []
        for dim, report in fairness_results[20].items():
            report = report.copy()
            report.insert(0, "demographic_dimension", dim)
            report = report.rename(columns={dim: "group_value"})
            k_20_reports.append(report)
        fairness_report_df = pd.concat(k_20_reports, ignore_index=True)
        fairness_report_df.to_csv(os.path.join(output_dir, "fairness_report.csv"), index=False)
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