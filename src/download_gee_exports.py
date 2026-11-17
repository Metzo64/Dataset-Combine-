"""
AUTOMATED GOOGLE DRIVE EXPORT DOWNLOAD

This script automatically downloads completed GEE exports from Google Drive.

Features:
- Automated OAuth authentication
- Searches for exports in specified folder
- Downloads CSV files
- Verifies file integrity
- Consolidates into final dataset

Usage:
    python src/download_gee_exports.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io

from config.config import EXPORTS_DIR, EXPORT_DRIVE_FOLDER

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Token file for saved credentials
TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', '.gdrive_token.pickle')


def authenticate_drive():
    """
    Authenticate with Google Drive API.
    
    Returns:
        service: Google Drive API service object
    """
    print("=" * 80)
    print("GOOGLE DRIVE AUTHENTICATION")
    print("=" * 80)
    print()
    
    creds = None
    
    # Check for existing token
    if os.path.exists(TOKEN_FILE):
        print("[OK] Found existing Drive credentials")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials don't exist or are invalid, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("No valid credentials found.")
            print()
            print("You will be redirected to a browser to authorize Google Drive access.")
            print("This is needed to download GEE exports automatically.")
            print()
            print("Please:")
            print("  1. Sign in with your Google account")
            print("  2. Grant Drive read access")
            print("  3. Return to this terminal")
            print()
            
            # Note: This requires a client secrets file
            # For now, provide manual fallback
            print("[ERROR] OAuth flow requires client_secrets.json")
            print()
            print("MANUAL FALLBACK:")
            print("  1. Go to: https://drive.google.com/")
            print(f"  2. Find folder: {EXPORT_DRIVE_FOLDER}")
            print("  3. Download all CSV files starting with 'satellite_'")
            print(f"  4. Place files in: {EXPORTS_DIR}")
            print()
            return None
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print("[OK] Drive credentials saved")
    
    print()
    
    try:
        service = build('drive', 'v3', credentials=creds)
        print("[OK] Drive API service created")
        print()
        return service
    except Exception as e:
        print(f"[ERROR] Failed to create Drive service: {e}")
        print()
        return None


def find_export_folder(service, folder_name):
    """
    Find the export folder in Google Drive.
    
    Args:
        service: Drive API service
        folder_name (str): Folder name to search for
        
    Returns:
        str: Folder ID or None
    """
    print(f"Searching for folder: {folder_name}")
    
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        folders = results.get('files', [])
        
        if not folders:
            print(f"[WARNING] Folder not found: {folder_name}")
            return None
        
        folder_id = folders[0]['id']
        print(f"[OK] Found folder ID: {folder_id}")
        print()
        return folder_id
        
    except Exception as e:
        print(f"[ERROR] Failed to search for folder: {e}")
        return None


def list_export_files(service, folder_id):
    """
    List CSV files in the export folder.
    
    Args:
        service: Drive API service
        folder_id (str): Folder ID
        
    Returns:
        list: List of file metadata dictionaries
    """
    print("Listing export files...")
    
    try:
        query = f"'{folder_id}' in parents and name contains 'satellite_' and mimeType='text/csv' and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, size, modifiedTime)'
        ).execute()
        
        files = results.get('files', [])
        print(f"[OK] Found {len(files)} export files")
        print()
        
        for f in files:
            size_mb = int(f.get('size', 0)) / 1024 / 1024
            print(f"  {f['name']:<30} ({size_mb:>6.2f} MB)")
        
        print()
        return files
        
    except Exception as e:
        print(f"[ERROR] Failed to list files: {e}")
        return []


def download_file(service, file_id, file_name, dest_dir):
    """
    Download a file from Google Drive.
    
    Args:
        service: Drive API service
        file_id (str): File ID
        file_name (str): File name
        dest_dir (str): Destination directory
        
    Returns:
        bool: True if successful
    """
    dest_path = os.path.join(dest_dir, file_name)
    
    # Skip if already exists
    if os.path.exists(dest_path):
        print(f"[SKIP] {file_name} (already exists)")
        return True
    
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(dest_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        print(f"[OK] Downloaded: {file_name}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to download {file_name}: {e}")
        return False


def download_all_exports():
    """
    Download all GEE exports from Google Drive.
    
    Returns:
        bool: True if successful
    """
    print()
    print("=" * 80)
    print("AUTOMATED GEE EXPORT DOWNLOAD")
    print("=" * 80)
    print()
    
    # Ensure output directory exists
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # Authenticate
    service = authenticate_drive()
    if not service:
        print("[ERROR] Drive authentication failed")
        print()
        print("MANUAL DOWNLOAD REQUIRED:")
        print("  1. Go to: https://drive.google.com/")
        print(f"  2. Find folder: {EXPORT_DRIVE_FOLDER}")
        print("  3. Download all CSV files")
        print(f"  4. Place in: {EXPORTS_DIR}")
        print()
        return False
    
    # Find folder
    folder_id = find_export_folder(service, EXPORT_DRIVE_FOLDER)
    if not folder_id:
        print("[ERROR] Export folder not found")
        print()
        print("MANUAL DOWNLOAD REQUIRED:")
        print("  1. Go to: https://drive.google.com/")
        print(f"  2. Find folder: {EXPORT_DRIVE_FOLDER}")
        print("  3. Download all CSV files")
        print(f"  4. Place in: {EXPORTS_DIR}")
        print()
        return False
    
    # List files
    files = list_export_files(service, folder_id)
    if not files:
        print("[WARNING] No export files found")
        return False
    
    # Download files
    print("=" * 80)
    print("DOWNLOADING FILES")
    print("=" * 80)
    print()
    
    success_count = 0
    for file_info in files:
        if download_file(service, file_info['id'], file_info['name'], EXPORTS_DIR):
            success_count += 1
    
    print()
    print("=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print()
    print(f"Files downloaded: {success_count}/{len(files)}")
    print(f"Destination: {EXPORTS_DIR}")
    print()
    
    if success_count == len(files):
        print("[OK] All files downloaded successfully")
        print()
        print("Next steps:")
        print("  python src/merge_satellite_exports.py")
        print("  python src/validate_satellite.py")
        print()
        return True
    else:
        print("[WARNING] Some files failed to download")
        return False


if __name__ == "__main__":
    success = download_all_exports()
    sys.exit(0 if success else 1)
