import pandas as pd
from src.data.preprocessor import ClaimPreprocessor

def main():
    print("Loading PROCESSED claims dataset...")
    df = pd.read_csv("data/processed/claims_processed.csv", low_memory=False)

    print("✅ Data loaded")
    print("Columns:", list(df.columns))

    preprocessor = ClaimPreprocessor()
    X, y = preprocessor.preprocess_data(df, fit=True)

    print("✅ Preprocessing complete")
    print("X shape:", X.shape)
    print("y shape:", y.shape)

if __name__ == "__main__":
    main()
