import numpy as np
import pandas as pd

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Log transforms (fix near-zero importance)
    df["billed_items_log"] = np.log1p(df["billed_items_count"])
    df["previous_claims_log"] = np.log1p(df["previous_claims_count"])

    # Age buckets
    df["age_bucket"] = pd.cut(
        df["patient_age"],
        bins=[0, 18, 30, 45, 60, 100],
        labels=["child", "young", "adult", "mid_age", "senior"]
    )

    # One-hot encode buckets
    df = pd.get_dummies(df, columns=["age_bucket"], drop_first=True)

    # Interaction feature
    df["claims_x_items"] = (
        df["previous_claims_log"] * df["billed_items_log"]
    )

    return df
