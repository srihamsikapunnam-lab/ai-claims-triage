"""
Train XGBoost model for fraud detection and save it with LIME explainer
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import lime
import lime.lime_tabular

print("🚀 Training XGBoost Model for Fraud Detection")
print("=" * 60)

# Load the unified claims data
data_path = Path("data/processed/unified_claims_v1.csv")
if not data_path.exists():
    print(f"❌ Data file not found: {data_path}")
    exit(1)

df = pd.read_csv(data_path)
print(f"✅ Loaded data: {df.shape}")
print(f"📊 Columns: {df.columns.tolist()}")

# Create fraud label if it doesn't exist (based on patterns)
if 'is_fraud' not in df.columns:
    # Create synthetic fraud labels based on suspicious patterns
    df['is_fraud'] = (
        (df['claimed_amount'] > df['claimed_amount'].quantile(0.95)) |
        ((df['length_of_stay'] < 2) & (df['claimed_amount'] > df['claimed_amount'].quantile(0.75)))
    ).astype(int)
    print("⚠️  Created synthetic fraud labels based on patterns")

print(f"🎯 Fraud rate: {df['is_fraud'].mean():.2%}")

# Clean data
print("\n🧹 Cleaning data...")

# Convert numeric columns to proper types
df['patient_age'] = pd.to_numeric(df['patient_age'], errors='coerce')
df['claimed_amount'] = pd.to_numeric(df['claimed_amount'], errors='coerce')

df = df.dropna(subset=['patient_age', 'claimed_amount', 'admission_date', 'discharge_date'])
df = df[df['patient_age'] > 0]
df = df[df['claimed_amount'] > 0]

print(f"✅ Clean data: {df.shape}")

# Feature engineering
print("\n🔧 Engineering features...")

# Calculate length_of_stay from dates
df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce')
df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')
df['length_of_stay'] = (df['discharge_date'] - df['admission_date']).dt.days
df['length_of_stay'] = df['length_of_stay'].fillna(1).clip(lower=0)

print(f"✅ Calculated length_of_stay for {len(df)} claims")

# Remove any rows with invalid dates
df = df[df['length_of_stay'] >= 0]

# Calculate derived features
df['claimed_per_day'] = df['claimed_amount'] / (df['length_of_stay'] + 1)
df['high_amount_flag'] = (df['claimed_amount'] > df['claimed_amount'].quantile(0.95)).astype(int)
df['short_stay_high_bill'] = (
    (df['length_of_stay'] < 2) & 
    (df['claimed_amount'] > df['claimed_amount'].median())
).astype(int)

# Encode categorical variables
encoders = {}

# Gender encoding
if 'gender' in df.columns:
    le_gender = LabelEncoder()
    df['gender_encoded'] = le_gender.fit_transform(df['gender'].fillna('Unknown'))
    encoders['gender'] = le_gender
    print(f"✅ Gender encoded: {list(le_gender.classes_)}")
else:
    df['gender_encoded'] = 0
    print("⚠️  Gender column not found, using default")

# Diagnosis encoding
if 'diagnosis_code' in df.columns:
    # Group rare diagnoses
    top_diagnoses = df['diagnosis_code'].value_counts().head(20).index
    df['diagnosis_group'] = df['diagnosis_code'].apply(
        lambda x: x if x in top_diagnoses else 'Other'
    )
    le_diagnosis = LabelEncoder()
    df['diagnosis_encoded'] = le_diagnosis.fit_transform(df['diagnosis_group'])
    encoders['diagnosis'] = le_diagnosis
    print(f"✅ Diagnosis encoded: {len(le_diagnosis.classes_)} categories")
else:
    df['diagnosis_encoded'] = 0
    print("⚠️  Diagnosis column not found, using default")

# Select features for model
feature_columns = [
    'patient_age',
    'claimed_amount',
    'length_of_stay',
    'claimed_per_day',
    'high_amount_flag',
    'short_stay_high_bill',
    'gender_encoded',
    'diagnosis_encoded'
]

print(f"\n📊 Features selected: {feature_columns}")

# Prepare X and y
X = df[feature_columns].copy()
y = df['is_fraud'].copy()

print(f"✅ Feature matrix: {X.shape}")
print(f"✅ Target vector: {y.shape}")
print(f"🎯 Final fraud rate: {y.mean():.2%}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Train set: {X_train.shape}, Test set: {X_test.shape}")
print(f"🎯 Train fraud rate: {y_train.mean():.2%}")
print(f"🎯 Test fraud rate: {y_test.mean():.2%}")

# Train XGBoost model
print("\n🤖 Training XGBoost model...")

# Calculate scale_pos_weight for imbalanced classes
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric='logloss'
)

xgb_model.fit(X_train, y_train)
print("✅ XGBoost model trained!")

# Evaluate model
print("\n📈 Evaluating model...")
train_pred = xgb_model.predict(X_train)
test_pred = xgb_model.predict(X_test)
train_proba = xgb_model.predict_proba(X_train)[:, 1]
test_proba = xgb_model.predict_proba(X_test)[:, 1]

train_auc = roc_auc_score(y_train, train_proba)
test_auc = roc_auc_score(y_test, test_proba)

print(f"🎯 Training AUC: {train_auc:.4f}")
print(f"🎯 Test AUC: {test_auc:.4f}")

print("\n📊 Test Set Classification Report:")
print(classification_report(y_test, test_pred, target_names=['Legitimate', 'Fraud']))

print("\n📊 Confusion Matrix:")
cm = confusion_matrix(y_test, test_pred)
print(cm)

# Feature importance
print("\n🔝 Feature Importance:")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': xgb_model.feature_importances_
}).sort_values('importance', ascending=False)
print(feature_importance)

# Create LIME explainer
print("\n🕵️ Creating LIME explainer...")
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    training_data=X_train.values,
    feature_names=feature_columns,
    class_names=['Legitimate', 'Fraud'],
    mode='classification',
    random_state=42
)
print("✅ LIME explainer created!")

# Test LIME on a sample
print("\n🧪 Testing LIME explanation on a sample prediction...")
test_idx = 0
instance = X_test.iloc[test_idx].values
explanation = lime_explainer.explain_instance(
    instance,
    xgb_model.predict_proba,
    num_features=5
)
print(f"Sample prediction: {xgb_model.predict_proba([instance])[0]}")
print("Top features:")
for feature, weight in explanation.as_list()[:5]:
    print(f"  {feature}: {weight:.3f}")

# Save model with all components
print("\n💾 Saving model...")
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)

# Save model without LIME explainer (will recreate on load)
model_data = {
    'model': xgb_model,
    'feature_names': feature_columns,
    'encoders': encoders,
    'training_data': X_train.values,  # Store training data to recreate LIME
    'model_type': 'XGBClassifier',
    'version': '2.0',
    'metrics': {
        'train_auc': train_auc,
        'test_auc': test_auc
    }
}

model_path = models_dir / "xgboost_fraud_model.joblib"
joblib.dump(model_data, model_path)
print(f"✅ Model saved to: {model_path}")

# Also save as the API-ready model
api_model_path = models_dir / "fraud_model_api_ready.joblib"
joblib.dump(model_data, api_model_path)
print(f"✅ API-ready model saved to: {api_model_path}")

print("\nℹ️  Note: LIME explainer will be recreated when model is loaded")

print("\n" + "=" * 60)
print("🎉 Training complete!")
print(f"📊 Model Type: XGBoost")
print(f"🎯 Test AUC: {test_auc:.4f}")
print(f"📝 Features: {len(feature_columns)}")
print(f"💾 Saved to: {model_path}")
print("=" * 60)
