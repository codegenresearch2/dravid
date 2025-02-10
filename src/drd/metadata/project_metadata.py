import os
import json
from datetime import datetime
import fnmatch
import xml.etree.ElementTree as ET
import mimetypes
from ..utils.utils import print_info, print_warning

# Import the get_file_metadata_prompt function
from ..prompts.file_metadata_desc_prompts import get_file_metadata_prompt
from ..api import call_dravid_api_with_pagination

class ProjectMetadataManager:
    def __init__(self, project_dir):
        self.project_dir = os.path.abspath(project_dir)
        self.metadata_file = os.path.join(self.project_dir, 'drd.json')
        self.metadata = self.load_metadata()
        self.ignore_patterns = self.get_ignore_patterns()
        self.binary_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'}

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return self.create_default_metadata()

    def create_default_metadata(self):
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
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def get_ignore_patterns(self):
        patterns = [
            '**/.git/**', '**/node_modules/**', '**/dist/**', '**/build/**',
            '**/__pycache__/**', '**/.venv/**', '**/.idea/**', '**/.vscode/**'
        ]

        for root, _, files in os.walk(self.project_dir):
            if '.gitignore' in files:
                gitignore_path = os.path.join(root, '.gitignore')
                rel_root = os.path.relpath(root, self.project_dir)
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if rel_root == '.':
                                patterns.append(line)
                            else:
                                patterns.append(os.path.join(rel_root, line))

        return patterns

    def should_ignore(self, path):
        try:
            path_str = str(path)
            abs_path = os.path.abspath(path_str)
            rel_path = os.path.relpath(abs_path, self.project_dir)

            if rel_path.startswith('..'):
                return True

            for pattern in self.ignore_patterns:
                if pattern.endswith('/'):
                    if rel_path.startswith(pattern) or rel_path.startswith(pattern[:-1]):
                        return True
                elif fnmatch.fnmatch(rel_path, pattern):
                    return True
            return False
        except Exception as e:
            print_warning(f"Error in should_ignore for path {path}: {str(e)}")
            return True

    # ... rest of the code remains the same ...

    def update_file_metadata(self, filename, file_type, content, description=None, exports=None, imports=None):
        self.metadata['project_info']['last_updated'] = datetime.now().isoformat()
        file_entry = next((f for f in self.metadata['key_files'] if f['path'] == filename), None)
        if file_entry is None:
            file_entry = {'path': filename}
            self.metadata['key_files'].append(file_entry)
        file_entry.update({
            'type': file_type,
            'summary': description or file_entry.get('summary', ''),
            'exports': exports or [],
            'imports': imports or []
        })
        self.save_metadata()

    # ... additional methods as needed ...