import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Load service account credentials from environment variable
credentials_json = os.environ['GDRIVE_SERVICE_ACCOUNT']
credentials_dict = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

# Build Drive API service
service = build('drive', 'v3', credentials=credentials)

# Get folder ID from environment
folder_id = os.environ['GDRIVE_FOLDER_ID']

# List files in folder
results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    orderBy='modifiedTime desc',
    fields='files(id, name, modifiedTime)'
).execute()

files = results.get('files', [])

if not files:
    print('No DPR files found in Google Drive folder.')
    exit(1)

# Get the most recent DPR file
latest_file = files[0]
file_id = latest_file['id']
file_name = latest_file['name']

print(f"Downloading: {file_name}")

# Download file
request = service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)

done = False
while not done:
    status, done = downloader.next_chunk()
    print(f"Download {int(status.progress() * 100)}%")

# Save to data folder
os.makedirs('data', exist_ok=True)
output_path = os.path.join('data', 'latest_dpr.xlsx')

with open(output_path, 'wb') as f:
    f.write(fh.getvalue())

print(f"✅ Downloaded to: {output_path}")
