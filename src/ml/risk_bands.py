import numpy as np

def assign_risk_band(prob):
    """
    Convert fraud probability into risk band
    """
    if prob < 0.4:
        return "Low Risk"
    elif prob < 0.7:
        return "Medium Risk"
    else:
        return "High Risk"


def predict_with_risk(model, X):
    """
    Returns probability + risk band
    """
    probs = model.predict_proba(X)[:, 1]

    results = []
    for p in probs:
        results.append({
            "fraud_probability": round(float(p), 4),
            "risk_band": assign_risk_band(p)
        })

    return results
