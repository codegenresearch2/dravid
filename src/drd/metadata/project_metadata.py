import os
import json
from datetime import datetime
import fnmatch
import xml.etree.ElementTree as ET
import mimetypes
from ..utils.utils import print_info, print_warning
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
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
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

    # ... rest of the code remains the same ...

    async def analyze_file(self, file_path):
        rel_path = os.path.relpath(file_path, self.project_dir)

        if self.is_binary_file(file_path):
            return {
                "path": rel_path,
                "type": "binary",
                "summary": "Binary or non-text file",
                "exports": [],
                "imports": []
            }

        if file_path.endswith('.md'):
            return None  # Skip markdown files

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            prompt = get_file_metadata_prompt(rel_path, content, json.dumps(self.metadata), json.dumps(self.metadata['directory_structure']))
            response = call_dravid_api_with_pagination(prompt, include_context=True)

            root = ET.fromstring(response)
            metadata = root.find('metadata')

            imports = metadata.find('imports').text.split(',') if metadata.find('imports').text != 'None' else []
            file_info = {
                "path": rel_path,
                "type": metadata.find('type').text,
                "summary": metadata.find('description').text,
                "exports": metadata.find('exports').text.split(',') if metadata.find('exports').text != 'None' else [],
                "imports": imports
            }

            dependencies = metadata.find('external_dependencies')
            if dependencies is not None:
                for dep in dependencies.findall('dependency'):
                    self.metadata['external_dependencies'].append(dep.text)

        except Exception as e:
            print_warning(f"Error analyzing file {file_path}: {str(e)}")
            file_info = {
                "path": rel_path,
                "type": "unknown",
                "summary": "Error occurred during analysis",
                "exports": [],
                "imports": []
            }

        return file_info

    # ... rest of the code remains the same ...