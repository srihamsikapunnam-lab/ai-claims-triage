import pandas as pd

class ClaimPreprocessor:
    def __init__(self):
        pass

    def preprocess_data(self, df: pd.DataFrame, fit: bool = True):
        # --- REQUIRED COLUMN ---
        if "PotentialFraud" not in df.columns:
            raise ValueError("PotentialFraud column missing")

        # Target
        y = df["PotentialFraud"]
        if y.dtype == object:
            y = y.map({"Yes": 1, "No": 0})

        # Features: ONLY numeric to avoid OOM
        X = df.drop(columns=["PotentialFraud"])
        X = X.select_dtypes(include=["number"]).fillna(0)

        return X, y

    def save_preprocessor(self, path: str):
        # Dummy save (required by run_preprocessing.py)
        with open(path, "w") as f:
            f.write("numeric_only_preprocessor")
