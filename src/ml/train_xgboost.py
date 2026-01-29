import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

X = pd.read_csv("data/processed/features_v2.csv")
y = pd.read_csv("data/processed/labels.csv").squeeze()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)

preds = model.predict(X_test)
print(classification_report(y_test, preds))

joblib.dump(model, "models/xgboost_model.pkl")
print("✅ XGBoost model saved")
