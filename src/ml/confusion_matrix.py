import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

# Load data
X = pd.read_csv("data/processed/features.csv")
y = pd.read_csv("data/processed/labels.csv").values.ravel()

# Load trained model
model = joblib.load("models/fraud_model.pkl")

# Predict
preds = model.predict(X)

# Output
print("Confusion Matrix:")
print(confusion_matrix(y, preds))

print("\nClassification Report:")
print(classification_report(y, preds))
