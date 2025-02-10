import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json
from datetime import datetime

# Assuming the project structure, adjust the import path as necessary
from src.drd.metadata.project_metadata import ProjectMetadataManager

class TestProjectMetadataManager(unittest.TestCase):

    def setUp(self):
        self.project_dir = '/fake/project/dir'
        self.manager = ProjectMetadataManager(self.project_dir)

    @patch('os.walk')
    def test_get_ignore_patterns(self, mock_walk):
        mock_walk.return_value = [
            ('/fake/project/dir', [], ['.gitignore']),
            ('/fake/project/dir/subfolder', [], ['.gitignore'])
        ]
        mock_open_calls = [
            mock_open(read_data="*.log\nnode_modules/\n").return_value,
            mock_open(read_data="*.tmp\n").return_value
        ]
        with patch('builtins.open', side_effect=mock_open_calls):
            patterns, message = self.manager.get_ignore_patterns()

        self.assertIn('*.log', patterns)
        self.assertIn('node_modules/', patterns)
        self.assertIn('subfolder/*.tmp', patterns)
        self.assertEqual(message, "Using .gitignore patterns for file exclusion.")

    def test_should_ignore(self):
        self.manager.ignore_patterns = [
            '*.log', 'node_modules/', 'subfolder/*.tmp']
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/test.log'), "test.log should be ignored")
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/node_modules/package.json'), "package.json should be ignored")
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/node_modules/subfolder/file.js'), "file.js should be ignored")
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/subfolder/test.tmp'), "test.tmp should be ignored")
        self.assertFalse(self.manager.should_ignore(
            '/fake/project/dir/src/main.py'), "main.py should not be ignored")
        self.assertFalse(self.manager.should_ignore(
            '/fake/project/dir/package.json'), "package.json should not be ignored")

    @patch('os.walk')
    def test_get_directory_structure(self, mock_walk):
        mock_walk.return_value = [
            ('/fake/project/dir', ['src'], ['README.md']),
            ('/fake/project/dir/src', [], ['main.py', 'utils.py'])
        ]
        structure = self.manager.get_directory_structure(self.project_dir)
        expected_structure = {
            'files': ['README.md'],
            'directories': ['src'],
            'src': {
                'files': ['main.py', 'utils.py']
            }
        }
        self.assertEqual(structure, expected_structure, "Directory structure does not match")

    def test_is_binary_file(self):
        self.assertTrue(self.manager.is_binary_file('test.exe'), "test.exe should be binary")
        self.assertTrue(self.manager.is_binary_file('image.png'), "image.png should be binary")
        self.assertFalse(self.manager.is_binary_file('script.py'), "script.py should not be binary")
        self.assertFalse(self.manager.is_binary_file('config.json'), "config.json should not be binary")

    @patch('src.drd.metadata.project_metadata.call_dravid_api_with_pagination')
    @patch('builtins.open', new_callable=mock_open, read_data='print("Hello, World!")')
    async def test_analyze_file(self, mock_file, mock_api_call):
        mock_api_call.return_value = '''
        <response>
          <metadata>
            <type>python</type>
            <description>A simple Python script</description>
            <exports>None</exports>
            <imports>None</imports>
          </metadata>
        </response>
        '''
        file_info = await self.manager.analyze_file('/fake/project/dir/script.py')
        self.assertEqual(file_info['path'], 'script.py', "File path does not match")
        self.assertEqual(file_info['type'], 'python', "File type does not match")
        self.assertEqual(file_info['summary'], 'A simple Python script', "File summary does not match")

    @patch('src.drd.metadata.project_metadata.ProjectMetadataManager.analyze_file')
    @patch('os.walk')
    async def test_build_metadata(self, mock_walk, mock_analyze_file):
        mock_walk.return_value = [
            ('/fake/project/dir', [], ['main.py', 'README.md'])
        ]
        mock_analyze_file.side_effect = [
            {
                'path': 'main.py',
                'type': 'python',
                'summary': 'Main Python script',
                'exports': ['main_function'],
                'imports': ['os']
            },
            None  # Simulating skipping README.md
        ]
        loader = MagicMock()
        metadata = await self.manager.build_metadata(loader)

        self.assertEqual(metadata['environment']['primary_language'], 'python', "Primary language does not match")
        self.assertEqual(len(metadata['key_files']), 1, "Number of key files does not match")
        self.assertEqual(metadata['key_files'][0]['path'], 'main.py', "Key file path does not match")