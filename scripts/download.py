import requests
import os
import zipfile
from pathlib import Path

def download_team_data():
    """Script for teammates to download data from Google Drive"""
    data_files = {
        'archive.zip': 'https://drive.google.com/file/d/1z7cboND9phtkZlCEkfi-8TNitPZwh6nJ/view?usp=drive_link',
        'archive (1).zip': 'https://drive.google.com/file/d/1Q84jdimHnkWPkCCVdLwc7BjZEDZ2PbNQ/view?usp=drive_link'
    }
    
    raw_path = Path('data/raw')
    raw_path.mkdir(parents=True, exist_ok=True)
    
    print("📥 Downloading team data from Google Drive...")
    
    for filename, url in data_files.items():
        file_path = raw_path / filename
        
        if not file_path.exists():
            print(f"Downloading {filename}...")
            # Download logic here
            download_from_gdrive(url, file_path)
        else:
            print(f"✅ {filename} already exists")
    
    print("🎉 Data download complete! Run: python src/data/data_loader.py")

def download_from_gdrive(url, output_path):
    """Download from Google Drive"""
    import gdown
    gdown.download(url, str(output_path), quiet=False)

if __name__ == "__main__":
    download_team_data()