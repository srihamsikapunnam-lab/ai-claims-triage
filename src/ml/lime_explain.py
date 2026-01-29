import joblib
import pandas as pd
import numpy as np
from lime.lime_tabular import LimeTabularExplainer

# Load data
X = pd.read_csv("data/processed/features_v2.csv")

# Load model
model = joblib.load("models/best_model.pkl")

def predict_fn(x):
    return model.predict_proba(x)

X_np = X.values

explainer = LimeTabularExplainer(
    training_data=X_np,
    feature_names=X.columns.tolist(),
    class_names=["Not Fraud", "Fraud"],
    mode="classification"
)

i = 0
sample = X_np[i]

exp = explainer.explain_instance(
    sample,
    predict_fn,
    num_features=10
)

print("LIME Explanation for sample", i)
for feature, weight in exp.as_list():
    print(f"{feature}: {weight}")
