import os
import json
from google.auth import default
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Try to use application default credentials first, fall back to OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Authenticate and return a Google Drive API service instance using ADC or gcloud."""
    try:
        # Use gcloud application-default credentials (already configured on this VM)
        creds, project = default(scopes=['https://www.googleapis.com/auth/drive'])
        if creds and hasattr(creds, 'refresh') and not creds.valid:
            creds.refresh(Request())
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"\n[Drive Upload] ERROR: Could not authenticate with Google Drive.")
        print(f"  Details: {e}")
        print(f"  Try running: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive")
        return None


def find_or_create_folder(service, folder_name, parent_id=None):
    """Find a folder by name under a parent, or create it if it doesn't exist."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    
    # Create the folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder['id']


def upload_file_to_folder(service, local_path, parent_folder_id):
    """Upload a single file to a specific Drive folder."""
    file_name = os.path.basename(local_path)
    
    # Determine mime type
    if local_path.endswith('.json'):
        mime = 'application/json'
    elif local_path.endswith('.ipynb'):
        mime = 'application/x-ipynb+json'
    else:
        mime = 'application/octet-stream'
    
    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id]
    }
    
    media = MediaFileUpload(local_path, mimetype=mime)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink'
    ).execute()
    
    return uploaded


def upload_project_folder(project_dir, topic_slug):
    """
    Upload the entire project folder to Google Drive, mirroring the structure:
    Drive: youtube-video-generator / [topic_slug] / [files...]
    """
    print("\n--- Uploading Project to Google Drive ---")
    
    service = get_drive_service()
    if not service:
        print("Skipping Drive upload (no credentials).")
        return False
    
    # Find or create the top-level 'youtube-video-generator' folder
    root_folder_id = find_or_create_folder(service, 'youtube-video-generator')
    print(f"  Found/created root folder: youtube-video-generator")
    
    # Find or create the project subfolder
    project_folder_id = find_or_create_folder(service, topic_slug, parent_id=root_folder_id)
    print(f"  Found/created project folder: {topic_slug}")
    
    # Upload all files in the project directory
    uploaded_files = []
    for filename in sorted(os.listdir(project_dir)):
        filepath = os.path.join(project_dir, filename)
        if not os.path.isfile(filepath):
            continue
        
        print(f"  Uploading {filename}...")
        result = upload_file_to_folder(service, filepath, project_folder_id)
        uploaded_files.append(result)
        
        if filename.endswith('.ipynb'):
            colab_url = f"https://colab.research.google.com/drive/{result['id']}"
            print(f"  -> Open in Colab: {colab_url}")
    
    print(f"\nAll {len(uploaded_files)} files uploaded to Drive!")
    return True
