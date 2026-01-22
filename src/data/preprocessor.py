import pandas as pd
import pickle
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


class ClaimPreprocessor:
    def __init__(self):
        self.pipeline = None
        self.feature_columns = None

    def preprocess_data(self, df: pd.DataFrame, fit: bool = True):
        """
        Input:
            df -> raw CMS Train dataframe

        Output:
            X_df -> processed feature dataframe
            y -> encoded target series (0/1)
        """

        # ---------- Safety checks ----------
        required_cols = ["Provider", "PotentialFraud"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"❌ Required column '{col}' not found")

        # ---------- Encode target ----------
        y_raw = df["PotentialFraud"]

        if y_raw.dtype == object:
            y = y_raw.map({"Yes": 1, "No": 0})
        else:
            y = y_raw.astype(int)

        if y.isnull().any():
            raise ValueError(
                "❌ Target contains unexpected values. Expected Yes/No or 0/1"
            )

        # ---------- Features ----------
        # KEEP Provider as a categorical feature
        X = df.drop(columns=["PotentialFraud"])

        categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
        numeric_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

        if not categorical_cols and not numeric_cols:
            raise ValueError("❌ No feature columns found after preprocessing")

        # ---------- Pipelines ----------
        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False
                    ),
                ),
            ]
        )

        self.pipeline = ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, numeric_cols),
                ("cat", categorical_pipeline, categorical_cols),
            ]
        )

        # ---------- Fit / Transform ----------
        if fit:
            X_processed = self.pipeline.fit_transform(X)
        else:
            X_processed = self.pipeline.transform(X)

        # ---------- Feature names ----------
        feature_names = []

        if numeric_cols:
            feature_names.extend(numeric_cols)

        if categorical_cols:
            cat_features = (
                self.pipeline.named_transformers_["cat"]
                .named_steps["onehot"]
                .get_feature_names_out(categorical_cols)
                .tolist()
            )
            feature_names.extend(cat_features)

        if len(feature_names) == 0:
            raise ValueError("❌ Feature matrix has zero columns after encoding")

        X_df = pd.DataFrame(X_processed, columns=feature_names)

        return X_df, y

    def save_preprocessor(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self.pipeline, f)
