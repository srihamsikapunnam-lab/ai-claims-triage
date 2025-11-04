import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataUnifier:
    def __init__(self):
        self.required_columns = [
            'claim_id', 'patient_age', 'gender', 'hospital_id', 
            'admission_date', 'discharge_date', 'diagnosis_code',
            'claimed_amount', 'billed_items_count', 'previous_claims_count',
            'insurer_id', 'doc_missing_flag', 'is_fraud'
        ]
    
    def unify_datasets(self, datasets):
        """Unify multiple datasets into a standardized format"""
        unified_data = []
        
        for dataset_name, df in datasets.items():
            try:
                standardized_df = self._standardize_dataset(df, dataset_name)
                if standardized_df is not None and not standardized_df.empty:
                    unified_data.append(standardized_df)
                    logger.info(f"Standardized {dataset_name}: {standardized_df.shape}")
            except Exception as e:
                logger.error(f"Error standardizing {dataset_name}: {e}")
        
        if unified_data:
            unified_df = pd.concat(unified_data, ignore_index=True, sort=False)
            logger.info(f"Final unified dataset: {unified_df.shape}")
            return unified_df
        else:
            logger.error("No datasets were successfully unified")
            return None
    
    def _standardize_dataset(self, df, dataset_name):
        """Standardize individual dataset to common format"""
        # Create a copy to avoid modifying original
        standardized = df.copy()
        
        # Map columns to standard names
        column_mapping = self._get_column_mapping(df.columns, dataset_name)
        standardized = standardized.rename(columns=column_mapping)
        
        # Ensure all required columns exist
        for col in self.required_columns:
            if col not in standardized.columns:
                standardized[col] = None
        
        # Handle fraud label - this is critical!
        standardized = self._handle_fraud_label(standardized, dataset_name)
        
        # Select only required columns
        available_columns = [col for col in self.required_columns if col in standardized.columns]
        standardized = standardized[available_columns]
        
        return standardized
    
    def _get_column_mapping(self, actual_columns, dataset_name):
        """Map actual column names to standard names"""
        mapping = {}
        actual_cols_lower = [col.lower().strip() for col in actual_columns]
        
        # Common column name variations
        variations = {
            'claim_id': ['claim_id', 'id', 'claimid', 'claim_number', 'patient id', 'beneid', 'provider'],
            'patient_age': ['age', 'patient_age', 'patient age', 'age ', ' age '],
            'gender': ['gender', 'sex', 'patient_gender'],
            'claimed_amount': ['amount', 'claimed_amount', 'claim_amount', 'total_amount', 'amount billed', 'amount  ', 'inscclaimamtreimbursed'],
            'diagnosis_code': ['diagnosis', 'diagnosis_code', 'icd_code', 'procedure_code', 'clmdiagnosiscode_1'],
            'is_fraud': ['fraud', 'is_fraud', 'fraud_flag', 'label', 'fraud_type', 'potentialfraud'],
            'admission_date': ['admission_date', 'date_admitted', 'date of encounter', 'admissiondt', 'claimstartdt'],
            'discharge_date': ['discharge_date', 'date_discharged', 'date of discharge', 'dischargedt', 'claimenddt']
        }
        
        for standard_col, possible_names in variations.items():
            for possible in possible_names:
                if possible in actual_cols_lower:
                    idx = actual_cols_lower.index(possible)
                    mapping[actual_columns[idx]] = standard_col
                    break
        
        return mapping
    
    def _handle_fraud_label(self, df, dataset_name):
        """Handle different fraud label formats"""
        if 'is_fraud' not in df.columns:
            return df
            
        # Convert fraud labels to binary
        fraud_col = df['is_fraud']
        
        # Handle different fraud label formats
        if fraud_col.dtype == 'object':
            # Handle "No Fraud" vs fraud types
            no_fraud_indicators = ['no fraud', 'no', 'false', '0', 'n', 'f', 'genuine']
            fraud_indicators = ['yes', 'true', 'fraud', '1', 'y', 't']
            
            # Convert to string and lowercase for comparison
            fraud_str = fraud_col.astype(str).str.lower().str.strip()
            
            # If it contains specific fraud types, mark as fraud (1)
            if fraud_str.isin(['phantom billing', 'wrong diagnosis', 'ghost enrollee', 'fake treatment', 'ghost patients', 'wrong diagnoses']).any():
                df['is_fraud'] = ~fraud_str.isin(no_fraud_indicators)
                df['is_fraud'] = df['is_fraud'].astype(int)
            else:
                # Simple binary mapping
                df['is_fraud'] = fraud_str.isin(fraud_indicators).astype(int)
        elif fraud_col.dtype == 'bool':
            df['is_fraud'] = fraud_col.astype(int)
        # If numeric, assume 1=fraud, 0=not fraud
        
        print(f"Dataset {dataset_name} - Fraud distribution: {df['is_fraud'].value_counts().to_dict()}")
        
        return df

def save_unified_data(df, output_path):
    """Save unified dataset to CSV"""
    df.to_csv(output_path, index=False)
    logger.info(f"Saved unified data to {output_path}")