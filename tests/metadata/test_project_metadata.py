from src.drd.metadata.project_metadata import ProjectMetadataManager
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class TestProjectMetadataManager(unittest.TestCase):

    def setUp(self):
        self.project_dir = '/fake/project/dir'
        self.manager = ProjectMetadataManager(self.project_dir)

    @patch('os.path.exists') 
    @patch('builtins.open', new_callable=mock_open, read_data='{"project_name": "Test Project"}') 
    def test_load_metadata(self, mock_file, mock_exists):
        mock_exists.return_value = True
        metadata = self.manager.load_metadata()
        self.assertEqual(metadata['project_name'], 'Test Project')
        mock_file.assert_called_once_with(os.path.join(self.project_dir, 'drd.json'), 'r')

    @patch('json.dump') 
    @patch('builtins.open', new_callable=mock_open) 
    def test_save_metadata(self, mock_file, mock_json_dump):
        self.manager.save_metadata()
        mock_file.assert_called_once_with(os.path.join(self.project_dir, 'drd.json'), 'w')
        mock_json_dump.assert_called_once()

    @patch.object(ProjectMetadataManager, 'save_metadata')
    def test_update_file_metadata(self, mock_save):
        self.manager.update_file_metadata(
            'test.py', 'python', 'print(\"Hello\")', 'A test Python file'
        )
        mock_save.assert_called_once()
        file_entry = next((f for f in self.manager.metadata['files'] if f['filename'] == 'test.py'), None)
        self.assertIsNotNone(file_entry)
        self.assertEqual(file_entry['type'], 'python')
        self.assertEqual(file_entry['content_preview'], 'print(\"Hello\")')
        self.assertEqual(file_entry['description'], 'A test Python file')

    @patch('os.path.exists') 
    @patch('builtins.open', new_callable=mock_open, read_data='print(\"Hello, World!\")')
    @patch.object(ProjectMetadataManager, 'update_file_metadata')
    def test_update_metadata_from_file(self, mock_update, mock_file, mock_exists):
        mock_exists.return_value = True
        result = self.manager.update_metadata_from_file('test.py')
        self.assertTrue(result)
        mock_update.assert_called_once_with('test.py', 'py', 'print(\"Hello, World!\")')
