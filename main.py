from src.data_loader import load_data, DataValidationError
from src.feature_engineering import create_payment_features


def main():
    print("=" * 60)
    print("BRITE SPARK 2026 — PROBLEM 6")
    print("THE OVERPAYMENT SIGNAL")
    print("=" * 60)

    try:
        # -----------------------------------------------------
        # Load data
        # -----------------------------------------------------
        cases, payments = load_data()

        print("\n✓ Data loading successful.")
        print(f"  Cases loaded:    {len(cases):,}")
        print(f"  Payments loaded: {len(payments):,}")

        # -----------------------------------------------------
        # Feature engineering
        # -----------------------------------------------------
        print("\nCreating payment features...")

        features = create_payment_features(
            cases,
            payments
        )
        c33248 = features[
        features["case_id"] == "C-33248"
        ]
        print("\nC-33248 feature snapshot:")
        print(c33248.to_string(index=False))

        print("✓ Feature engineering successful.")
        print(f"  Feature rows:    {len(features):,}")
        print(f"  Feature columns: {len(features.columns):,}")

        print("\nFeature columns:")
        for column in features.columns:
            print(f"  - {column}")

    except FileNotFoundError as error:
        print(f"\nERROR: {error}")

    except DataValidationError as error:
        print(f"\nDATA VALIDATION ERROR: {error}")


if __name__ == "__main__":
    main()