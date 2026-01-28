# src/run_preprocessing.py

import pandas as pd
from src.data.preprocessor import ClaimPreprocessor
import os


def main():
    print("Loading raw CMS claims dataset...")

    df = pd.read_csv(
        "data/processed/unified_claims_v1.csv"

    )

    print("✅ Data loaded")
    print("Columns:", df.columns.tolist())

    preprocessor = ClaimPreprocessor()

    X, y = preprocessor.preprocess_data(df, fit=True)

    # ---------- Ensure output directories ----------
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # ---------- Save outputs ----------
    X.to_csv("data/processed/features.csv", index=False)
    y.to_csv("data/processed/labels.csv", index=False)

    preprocessor.save_preprocessor("models/preprocessor.pkl")

    print("✅ Preprocessing complete")
    print("Feature shape:", X.shape)


if __name__ == "__main__":
    main()
