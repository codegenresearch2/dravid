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
        self.file_extensions = {
            'binary': {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'},
            'text': {'.*', '.json'}
        }

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return self.initialize_metadata()

    def initialize_metadata(self):
        return {
            'project_info': {
                'name': os.path.basename(self.project_dir),
                'version': '1.0.0',
                'description': '',
                'last_updated': datetime.now().isoformat()
            },
            'environment': {
                'primary_language': '',
                'other_languages': [],
                'primary_framework': '',
                'runtime_version': ''
            },
            'directory_structure': {},
            'files': [],
            'external_dependencies': [],
            'dev_server': {
                'start_command': ''
            }
        }

    def save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def get_ignore_patterns(self):
        # ... (remains the same)

    def should_ignore(self, path):
        # ... (remains the same)

    def get_directory_structure(self, start_path):
        # ... (remains the same)

    def get_file_type(self, file_path):
        _, extension = os.path.splitext(file_path)
        for file_type, extensions in self.file_extensions.items():
            if extension.lower() in extensions:
                return file_type
        mime_type, _ = mimetypes.guess_type(file_path)
        return 'text' if mime_type and mime_type.startswith('text') else 'binary'

    async def analyze_file(self, file_path):
        rel_path = os.path.relpath(file_path, self.project_dir)
        file_type = self.get_file_type(file_path)

        if file_type == 'binary':
            return {
                'path': rel_path,
                'type': 'binary',
                'summary': 'Binary or non-text file',
                'exports': [],
                'imports': []
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

            file_info = {
                'path': rel_path,
                'type': metadata.find('type').text,
                'summary': metadata.find('description').text,
                'exports': metadata.findtext('exports', '').split(','),
                'imports': metadata.findtext('imports', '').split(',')
            }

            dependencies = metadata.find('external_dependencies')
            if dependencies is not None:
                for dep in dependencies.findall('dependency'):
                    self.metadata['external_dependencies'].append(dep.text)

        except Exception as e:
            print_warning(f'Error analyzing file {file_path}: {str(e)}')
            file_info = {
                'path': rel_path,
                'type': 'unknown',
                'summary': 'Error occurred during analysis',
                'exports': [],
                'imports': []
            }

        return file_info

    async def build_metadata(self, loader):
        # ... (remains the same)

    def remove_file_metadata(self, filename):
        self.metadata['project_info']['last_updated'] = datetime.now().isoformat()
        self.metadata['files'] = [f for f in self.metadata['files'] if f['path'] != filename]
        self.save_metadata()

    def get_file_metadata(self, filename):
        return next((f for f in self.metadata['files'] if f['path'] == filename), None)

    def get_project_context(self):
        return json.dumps(self.metadata, indent=2)

    def add_external_dependency(self, dependency):
        if dependency not in self.metadata['external_dependencies']:
            self.metadata['external_dependencies'].append(dependency)
            self.save_metadata()

    def update_environment_info(self, primary_language, other_languages, primary_framework, runtime_version):
        self.metadata['environment'].update({
            'primary_language': primary_language,
            'other_languages': other_languages,
            'primary_framework': primary_framework,
            'runtime_version': runtime_version
        })
        self.save_metadata()

    def update_file_metadata(self, filename, file_type, description=None, exports=None, imports=None):
        self.metadata['project_info']['last_updated'] = datetime.now().isoformat()
        file_entry = next((f for f in self.metadata['files'] if f['path'] == filename), None)
        if file_entry is None:
            file_entry = {'path': filename}
            self.metadata['files'].append(file_entry)
        file_entry.update({
            'type': file_type,
            'summary': description or file_entry.get('summary', ''),
            'exports': exports or [],
            'imports': imports or []
        })
        self.save_metadata()


The changes made to the code include:

1. Enhanced XML response structure:
   - The `analyze_file` method now returns a more structured dictionary with clear keys for each piece of metadata.

2. Improved metadata handling for files:
   - Added a `get_file_type` method to determine the type of a file based on its extension and MIME type.
   - Updated the `analyze_file` method to handle files of different types, providing appropriate metadata.
   - Skipped markdown files during analysis.

3. Consistent naming in metadata fields:
   - Renamed the 'key_files' field in the metadata dictionary to 'files' for consistency.
   - Updated the `update_file_metadata` method to accept a 'description' parameter instead of 'content' for better clarity.