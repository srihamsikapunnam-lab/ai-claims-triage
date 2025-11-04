from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Model configuration
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Feature configuration
REQUIRED_COLUMNS = [
    'claim_id', 'patient_age', 'gender', 'hospital_id', 
    'admission_date', 'discharge_date', 'diagnosis_code',
    'claimed_amount', 'billed_items_count', 'previous_claims_count',
    'insurer_id', 'doc_missing_flag', 'is_fraud'
]

# Training configuration
MODEL_PARAMS = {
    'logistic_regression': {
        'max_iter': 1000,
        'random_state': RANDOM_STATE
    },
    'random_forest': {
        'n_estimators': 100,
        'random_state': RANDOM_STATE
    },
    'xgboost': {
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1,
        'random_state': RANDOM_STATE
    },
    'lightgbm': {
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1,
        'random_state': RANDOM_STATE
    }
}
