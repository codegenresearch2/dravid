import logging
import json
import os
from datetime import datetime

class ProjectMetadataManager:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.metadata_file = os.path.join(self.project_dir, 'drd.json')
        self.metadata = self.load_metadata()

    def load_metadata(self):
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            else:
                logging.warning(f"Metadata file {self.metadata_file} does not exist. Creating a new one.")
                return self.create_default_metadata()
        except json.JSONDecodeError:
            logging.error(f"Error: Invalid JSON content in {self.metadata_file}. Creating a new one.")
            return self.create_default_metadata()

    def create_default_metadata(self):
        return {
            "project_name": os.path.basename(self.project_dir),
            "last_updated": "",
            "files": [],
            "dev_server": {
                "start_command": "",
                "framework": "",
                "language": ""
            }
        }

    def save_metadata(self):
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logging.info(f"Metadata saved to {self.metadata_file}")
        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}")

    # Rest of the class methods remain the same as they are already following the rules

# Test cases remain the same as they are already following the rules