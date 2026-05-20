#!/usr/bin/env python3
"""
Download Latest DPR from Google Drive
======================================

This script downloads the most recent DPR file from a specific Google Drive folder.
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Configuration
GDRIVE_CREDENTIALS_FILE = 'gdrive_credentials.json'
GDRIVE_FOLDER_ID = os.environ.get('GDRIVE_FOLDER_ID', 'YOUR_FOLDER_ID_HERE')
OUTPUT_FILE = 'latest_dpr.xlsx'

# Google Drive API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def authenticate():
    """Authenticate with Google Drive using service account."""
    print("🔐 Authenticating with Google Drive...")
    
    credentials = service_account.Credentials.from_service_account_file(
        GDRIVE_CREDENTIALS_FILE,
        scopes=SCOPES
    )
    
    service = build('drive', 'v3', credentials=credentials)
    print("✅ Authentication successful")
    
    return service


def get_latest_dpr(service, folder_id):
    """Get the most recent DPR file from specified folder."""
    print(f"📂 Searching for latest DPR in folder: {folder_id}")
    
    # Query for Excel files in the folder
    query = f"'{folder_id}' in parents and (name contains 'DPR' or name contains 'dpr')"
    query += " and (mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
    query += " or mimeType='application/vnd.ms-excel')"
    query += " and trashed=false"
    
    results = service.files().list(
        q=query,
        orderBy='modifiedTime desc',
        pageSize=1,
        fields='files(id, name, modifiedTime)'
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        print("❌ No DPR files found in folder")
        raise FileNotFoundError("No DPR files found in Google Drive folder")
    
    latest_file = files[0]
    print(f"✅ Found latest DPR: {latest_file['name']}")
    print(f"📅 Last modified: {latest_file['modifiedTime']}")
    
    return latest_file


def download_file(service, file_id, file_name, output_path):
    """Download file from Google Drive."""
    print(f"⬇️  Downloading {file_name}...")
    
    request = service.files().get_media(fileId=file_id)
    
    fh = io.FileIO(output_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"   Progress: {int(status.progress() * 100)}%")
    
    print(f"✅ Downloaded to: {output_path}")


def main():
    """Main execution function."""
    print("="*60)
    print("ONE APEX - DOWNLOAD LATEST DPR FROM GOOGLE DRIVE")
    print("="*60)
    print()
    
    try:
        # Authenticate
        service = authenticate()
        
        # Get latest DPR file info
        latest_file = get_latest_dpr(service, GDRIVE_FOLDER_ID)
        
        # Download the file
        download_file(
            service,
            latest_file['id'],
            latest_file['name'],
            OUTPUT_FILE
        )
        
        # Save metadata
        metadata = {
            'file_name': latest_file['name'],
            'file_id': latest_file['id'],
            'modified_time': latest_file['modifiedTime'],
            'download_time': str(pd.Timestamp.now())
        }
        
        with open('dpr_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print()
        print("="*60)
        print("✅ DPR DOWNLOAD COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    import pandas as pd
    main()
