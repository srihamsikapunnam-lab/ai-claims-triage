import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class ClaimPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def preprocess_data(self, df):
        """Main preprocessing pipeline"""
        logger.info("Starting data preprocessing")
        
        # Create a copy to avoid modifying original
        processed_df = df.copy()
        
        # Handle dates and create new features
        processed_df = self._handle_dates(processed_df)
        
        # Feature engineering
        processed_df = self._feature_engineering(processed_df)
        
        # Handle missing values
        processed_df = self._handle_missing_values(processed_df)
        
        # Encode categorical variables
        processed_df = self._encode_categoricals(processed_df)
        
        # Select final features
        feature_df = self._select_features(processed_df)
        
        logger.info(f"Preprocessing complete. Final features: {feature_df.shape}")
        return feature_df, processed_df
    
    def _handle_dates(self, df):
        """Handle date columns and create date-based features"""
        df = df.copy()
        
        print("Date columns in dataframe:", [col for col in df.columns if 'date' in col.lower()])
        
        # Convert to datetime - handle multiple date column name variations
        date_column_variations = {
            'admission_date': ['admission_date', 'date_admitted', 'date of encounter', 'admissiondt', 'claimstartdt'],
            'discharge_date': ['discharge_date', 'date_discharged', 'date of discharge', 'dischargedt', 'claimenddt']
        }
        
        for standard_col, possible_names in date_column_variations.items():
            for possible in possible_names:
                if possible in df.columns:
                    print(f"Converting {possible} to datetime as {standard_col}")
                    df[standard_col] = pd.to_datetime(df[possible], errors='coerce')
                    break
            else:
                # If no matching column found, create empty datetime column
                df[standard_col] = pd.NaT
        
        # Calculate length of stay only if we have valid dates
        if 'admission_date' in df.columns and 'discharge_date' in df.columns:
            print("Calculating length of stay...")
            # Ensure both columns are datetime
            df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce')
            df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')
            
            # Calculate length of stay
            mask = df['admission_date'].notna() & df['discharge_date'].notna()
            df.loc[mask, 'length_of_stay'] = (df.loc[mask, 'discharge_date'] - df.loc[mask, 'admission_date']).dt.days
            df['length_of_stay'] = df['length_of_stay'].fillna(0)
            df['length_of_stay'] = df['length_of_stay'].clip(lower=0)
            
            print(f"Length of stay stats: min={df['length_of_stay'].min()}, max={df['length_of_stay'].max()}")
        
        return df
    
    def _feature_engineering(self, df):
        """Create new features from existing data"""
        df = df.copy()
        
        # Convert claimed_amount to numeric, handling strings with commas and spaces
        if 'claimed_amount' in df.columns:
            print("Converting claimed_amount to numeric...")
            
            # Handle string formatting (commas, spaces, currency symbols)
            if df['claimed_amount'].dtype == 'object':
                print("Detected string amounts, cleaning...")
                # Remove commas, spaces, and currency symbols
                df['claimed_amount'] = df['claimed_amount'].astype(str).str.replace(',', '').str.replace(' ', '').str.replace('$', '')
            
            df['claimed_amount'] = pd.to_numeric(df['claimed_amount'], errors='coerce')
            
            # Fill NaN values with median
            if df['claimed_amount'].notna().any():
                median_val = df['claimed_amount'].median()
                df['claimed_amount'] = df['claimed_amount'].fillna(median_val)
                print(f"Claimed amount stats: min={df['claimed_amount'].min()}, max={df['claimed_amount'].max()}, median={median_val}")
            else:
                df['claimed_amount'] = 0
                print("Warning: All claimed_amount values are NaN, setting to 0")
        
        # Claimed amount per day
        if 'length_of_stay' in df.columns and 'claimed_amount' in df.columns:
            print("Calculating claimed_per_day...")
            # Ensure both are numeric
            df['length_of_stay'] = pd.to_numeric(df['length_of_stay'], errors='coerce').fillna(0)
            df['claimed_per_day'] = df['claimed_amount'] / (df['length_of_stay'] + 1)  # +1 to avoid division by zero
            print(f"Claimed per day stats: min={df['claimed_per_day'].min()}, max={df['claimed_per_day'].max()}")
        
        # Find additional amount columns if claimed_amount is missing or zero
        amount_columns = [col for col in df.columns if 'amount' in col.lower() or 'billed' in col.lower() or 'reimbursed' in col.lower()]
        if amount_columns and ('claimed_amount' not in df.columns or df['claimed_amount'].sum() == 0):
            for amt_col in amount_columns:
                if amt_col != 'claimed_amount':
                    # Clean string formatting for alternative amount columns too
                    temp_amount = df[amt_col]
                    if temp_amount.dtype == 'object':
                        temp_amount = temp_amount.astype(str).str.replace(',', '').str.replace(' ', '').str.replace('$', '')
                    
                    df['claimed_amount'] = pd.to_numeric(temp_amount, errors='coerce')
                    if df['claimed_amount'].notna().any():
                        df['claimed_amount'] = df['claimed_amount'].fillna(df['claimed_amount'].median())
                        print(f"Using {amt_col} as claimed_amount")
                        break
        
        # Age groups


        # Amount to billed items ratio
        if 'claimed_amount' in df.columns and 'billed_items_count' in df.columns:
            print("Calculating amount_per_item...")
            df['billed_items_count'] = pd.to_numeric(df['billed_items_count'], errors='coerce').fillna(1)
            df['amount_per_item'] = df['claimed_amount'] / (df['billed_items_count'] + 1)
        
        return df

    def _handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        df = df.copy()
        
        print("Handling missing values...")
        
        # First, convert all potential numeric columns
        numeric_candidates = ['patient_age', 'claimed_amount', 'billed_items_count', 
                             'previous_claims_count', 'length_of_stay', 'claimed_per_day']
        
        for col in numeric_candidates:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Numerical columns - fill with median
        numerical_cols = ['patient_age', 'claimed_amount', 'billed_items_count', 
                         'previous_claims_count', 'length_of_stay', 'claimed_per_day']
        for col in numerical_cols:
            if col in df.columns:
                if df[col].notna().any():
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = 0
        
        # Categorical columns - fill with mode
        categorical_cols = ['gender', 'diagnosis_code', 'hospital_id', 'insurer_id']
        for col in categorical_cols:
            if col in df.columns:
                if not df[col].mode().empty:
                    df[col] = df[col].fillna(df[col].mode()[0])
                else:
                    df[col] = df[col].fillna('unknown')
        
        # Boolean columns
        if 'doc_missing_flag' in df.columns:
            df['doc_missing_flag'] = df['doc_missing_flag'].fillna(False)
        
        # Handle target variable
        if 'is_fraud' in df.columns:
            # Map fraud indicators to binary
            fraud_indicators = ['fraud', 'yes', 'true', '1', 1, True]
            df['is_fraud'] = df['is_fraud'].astype(str).str.lower().isin([str(x).lower() for x in fraud_indicators])
            df['is_fraud'] = df['is_fraud'].fillna(False).astype(int)
            print(f"Fraud distribution: {df['is_fraud'].value_counts()}")
        
        return df
    
    def _encode_categoricals(self, df):
        """Encode categorical variables"""
        df = df.copy()
        
        print("Encoding categorical variables...")
        
        categorical_cols = ['gender', 'diagnosis_code', 'hospital_id', 'insurer_id', 'age_group']
        
        for col in categorical_cols:
            if col in df.columns:
                # Handle NaN values before encoding - different approach for categorical vs regular columns
                if col == 'age_group' and pd.api.types.is_categorical_dtype(df[col]):
                    # For categorical age_group, add 'unknown' category
                    df[col] = df[col].cat.add_categories('unknown')
                    df[col] = df[col].fillna('unknown')
                else:
                    # For regular columns
                    df[col] = df[col].fillna('unknown')
                
                # Only encode if we have multiple values
                if df[col].nunique() > 1:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
                    print(f"Encoded {col} with {len(le.classes_)} classes")
                else:
                    # If only one value, set to 0
                    df[col] = 0
                    print(f"Column {col} has only one value, setting to 0")
        
        return df
    
    def _select_features(self, df):
        """Select final features for modeling"""
        feature_columns = [
            'patient_age', 'gender', 'hospital_id', 'diagnosis_code',
            'claimed_amount', 'billed_items_count', 'previous_claims_count',
            'insurer_id', 'doc_missing_flag', 'length_of_stay', 'claimed_per_day',
            'amount_per_item'
        ]
        
        # Only include columns that exist in the dataframe
        available_features = [col for col in feature_columns if col in df.columns]
        self.feature_names = available_features
        
        print(f"Selected features: {available_features}")
        
        return df[available_features]
    
    def get_train_test_split(self, features, target, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        # Ensure target is properly formatted
        target = target.astype(int)
        
        return train_test_split(
            features, target, 
            test_size=test_size, 
            random_state=random_state, 
            stratify=target
        )
    
    def save_preprocessor(self, filepath):
        """Save preprocessor object"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'label_encoders': self.label_encoders,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, f)
        logger.info(f"Preprocessor saved to {filepath}")
    
    def load_preprocessor(self, filepath):
        """Load preprocessor object"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.label_encoders = data['label_encoders']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
        logger.info(f"Preprocessor loaded from {filepath}")