"""
Generate confusion matrix for best trained model
"""

import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report

def main():
    # Load test data
    data_dir = Path("data/processed")

    X_test = np.load(data_dir / "X_test.npy")
    y_test = np.load(data_dir / "y_test.npy")

    # Load best model
    with open("models/best_model.pkl", "rb") as f:
        model = pickle.load(f)

    # IMPORTANT FIX 👇
    # Use underlying sklearn model
    y_pred = model.model.predict(X_test)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    print("\nCONFUSION MATRIX")
    print("================")
    print(cm)

    print("\nCLASSIFICATION REPORT")
    print("=====================")
    print(classification_report(y_test, y_pred, digits=4))

if __name__ == "__main__":
    main()
