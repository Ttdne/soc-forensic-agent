import os
import time
import requests
import urllib3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def execute(url: str, file_path: str, state_dir: str = None, **kwargs):
    try:
        # Set up a session
        session = requests.Session()
        session.trust_env = False  # Avoid using environment's proxies

        # Load PAT from environment
        pat = os.getenv('CONFLUENCE_PAT')
        if not pat:
            raise ValueError("Personal Access Token (PAT) not found in environment variables")

        headers = {
            'Authorization': f'Bearer {pat}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = session.get(
            url,
            headers=headers,
            verify=False  # Disable SSL verification for testing
        )

        if response.status_code == 200:
            # Determine the state directory
            if state_dir is None:
                timestamp = str(int(time.time()))
                state_dir = os.path.join("./test_environment", timestamp)
            os.makedirs(state_dir, exist_ok=True)

            # Normalize and construct the full file path
            file_path = os.path.normpath(file_path).lstrip(os.sep)
            full_file_path = os.path.join(state_dir, file_path)

            # Ensure the directory for the file exists
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

            with open(full_file_path, 'wb') as file:
                file.write(response.content)
            
            return {
                "tool": "file_download",
                "success": True,
                "full_file_path": file_path
            }
        else:
            return {
                "tool": "file_download",
                "success": False,
                "status_code": response.status_code,
                "error": "Failed to download file",
                "response_content": response.content.decode('utf-8', errors='replace')
            }

    except requests.exceptions.RequestException as e:
        return {
            "tool": "file_download",
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "tool": "file_download",
            "success": False,
            "error": str(e)
        }