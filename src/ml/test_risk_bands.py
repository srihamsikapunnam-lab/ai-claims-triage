import joblib
import numpy as np

# Load trained model
model = joblib.load("models/best_model.pkl")

# Dummy test probabilities (to show all bands)
test_probs = [0.12, 0.35, 0.55, 0.72, 0.91]

def risk_band(p):
    if p >= 0.8:
        return "High Risk"
    elif p >= 0.5:
        return "Medium Risk"
    else:
        return "Low Risk"

for i, p in enumerate(test_probs):
    print(f"Claim {i}: Probability={p:.2f} → {risk_band(p)}")
