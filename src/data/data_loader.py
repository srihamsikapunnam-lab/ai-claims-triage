import pandas as pd
import zipfile
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir="../../data/raw"):  # Changed path
        self.data_dir = Path(data_dir)
        self.extracted_dir = self.data_dir / "extracted"
        
    def load_kaggle_datasets(self):
        """Load and extract Kaggle datasets from zip files"""
        datasets = {}
        
        # Create extracted directory if it doesn't exist
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        # Look for zip files in raw data directory
        zip_files = list(self.data_dir.glob("*.zip"))
        
        print(f"Looking for zip files in: {self.data_dir}")  # Debug
        print(f"Found zip files: {zip_files}")  # Debug
        
        if not zip_files:
            logger.warning(f"No zip files found in {self.data_dir}")
            # Let's check what files ARE there
            all_files = list(self.data_dir.glob("*"))
            print(f"All files in directory: {all_files}")
            return datasets
            
        for zip_path in zip_files:
            dataset_name = zip_path.stem
            extract_path = self.extracted_dir / dataset_name
            
            try:
                # Extract zip file
                print(f"Extracting {zip_path} to {extract_path}")  # Debug
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                logger.info(f"Extracted {dataset_name} to {extract_path}")
                
                # Load CSV files from extracted directory
                csv_files = list(extract_path.glob("**/*.csv"))  # Search recursively
                print(f"Found CSV files: {csv_files}")  # Debug
                
                for csv_file in csv_files:
                    df_name = csv_file.stem
                    try:
                        print(f"Loading CSV: {csv_file}")  # Debug
                        df = pd.read_csv(csv_file)
                        datasets[f"{dataset_name}_{df_name}"] = df
                        logger.info(f"Loaded {df_name} with shape {df.shape}")
                        print(f"Columns: {df.columns.tolist()}")  # Debug
                    except Exception as e:
                        logger.error(f"Error loading {csv_file}: {e}")
                        print(f"Error loading {csv_file}: {e}")  # Debug
                        
            except Exception as e:
                logger.error(f"Error extracting {zip_path}: {e}")
                print(f"Error extracting {zip_path}: {e}")  # Debug
                
        return datasets
    
    def get_combined_dataset(self):
        """Combine all loaded datasets into a single dataframe"""
        datasets = self.load_kaggle_datasets()
        
        if not datasets:
            logger.error("No datasets loaded. Please check your data files.")
            return None
            
        # Combine all datasets
        combined_df = pd.concat(datasets.values(), ignore_index=True)
        logger.info(f"Combined dataset shape: {combined_df.shape}")
        
        return combined_df

def main():
    """Test function for data loading"""
    loader = DataLoader()
    datasets = loader.load_kaggle_datasets()
    print(f"Loaded {len(datasets)} datasets")
    
    for name, df in datasets.items():
        print(f"{name}: {df.shape}")

if __name__ == "__main__":
    main()