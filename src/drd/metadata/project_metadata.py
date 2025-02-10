import os
import json
from datetime import datetime
import fnmatch
import xml.etree.ElementTree as ET
import mimetypes
from ..prompts.file_metadata_desc_prompts import get_file_metadata_prompt
from ..api import call_dravid_api_with_pagination
from ..utils.utils import print_info, print_warning

class ProjectMetadataManager:
    def __init__(self, project_dir):
        self.project_dir = os.path.abspath(project_dir)
        self.metadata_file = os.path.join(self.project_dir, 'drd.json')
        self.metadata = self.load_metadata()
        self.ignore_patterns = self.get_ignore_patterns()
        self.binary_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'}

    def load_metadata(self):
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            else:
                return self.initialize_metadata()
        except Exception as e:
            print_warning(f"Error loading metadata: {str(e)}")
            return self.initialize_metadata()

    def initialize_metadata(self):
        return {
            "project_info": {
                "name": os.path.basename(self.project_dir),
                "version": "1.0.0",
                "description": "",
                "last_updated": datetime.now().isoformat()
            },
            "environment": {
                "primary_language": "",
                "other_languages": [],
                "primary_framework": "",
                "runtime_version": ""
            },
            "directory_structure": {},
            "key_files": [],
            "external_dependencies": [],
            "dev_server": {
                "start_command": ""
            }
        }

    def save_metadata(self):
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print_warning(f"Error saving metadata: {str(e)}")

    def get_ignore_patterns(self):
        patterns = [
            '**/.git/**', '**/node_modules/**', '**/dist/**', '**/build/**',
            '**/__pycache__/**', '**/.venv/**', '**/.idea/**', '**/.vscode/**'
        ]

        for root, _, files in os.walk(self.project_dir):
            if '.gitignore' in files:
                gitignore_path = os.path.join(root, '.gitignore')
                rel_root = os.path.relpath(root, self.project_dir)
                try:
                    with open(gitignore_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if rel_root == '.':
                                    patterns.append(line)
                                else:
                                    patterns.append(os.path.join(rel_root, line))
                except Exception as e:
                    print_warning(f"Error reading .gitignore file: {str(e)}")

        return patterns

    # Rest of the code remains the same as it is already clear and follows good practices