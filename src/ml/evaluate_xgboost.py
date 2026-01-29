import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load data
X = pd.read_csv("data/processed/features_v2.csv")
y = pd.read_csv("data/processed/labels.csv").squeeze()

# Same split as training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Load model
model = joblib.load("models/xgboost_model.pkl")

# Predict
preds = model.predict(X_test)

# Metrics
acc = accuracy_score(y_test, preds)

print("✅ XGBOOST MODEL PERFORMANCE")
print("--------------------------------")
print(f"Accuracy : {acc:.4f}")
print()
print(classification_report(y_test, preds))
