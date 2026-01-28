import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import pickle
from pathlib import Path

def main():
    print("Loading features and labels...")
    X = pd.read_csv("data/processed/features.csv")
    y = pd.read_csv("data/processed/labels.csv").squeeze()

    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    print("Evaluating model...")
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    Path("models").mkdir(exist_ok=True)

    with open("models/fraud_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("✅ Model saved to models/fraud_model.pkl")

if __name__ == "__main__":
    main()
