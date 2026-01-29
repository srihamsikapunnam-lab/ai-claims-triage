import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

# Load engineered features
X = pd.read_csv("data/processed/features_v2.csv")
y = pd.read_csv("data/processed/labels.csv").values.ravel()

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
from xgboost import XGBClassifier
import joblib
import numpy as np

# load data (already in your file)
# X_train, X_test, y_train, y_test

scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

model = XGBClassifier(
    n_estimators=400,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)
joblib.dump(model, "models/best_model.pkl")

print("✅ XGBoost trained and saved as final model")

