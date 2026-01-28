import pandas as pd
import joblib

# Load processed features
X = pd.read_csv("data/processed/features.csv")

# Load best model
model = joblib.load("models/best_model.pkl")

# IMPORTANT: wrapper uses predict_proba internally
if hasattr(model, "predict"):
    preds = model.predict(X)
else:
    preds = (model.model.predict_proba(X)[:, 1] > 0.5).astype(int)

# Show prediction distribution
print("Prediction counts:")
print(pd.Series(preds).value_counts())
