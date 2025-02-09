import unittest\\\nfrom unittest.mock import patch, mock_open, MagicMock\\\nimport os, sys, json, datetime\\\n\\n# Add the project root to the Python path\\\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))\\\\\n\\n\\nclass TestProjectMetadataManager(unittest.TestCase):\\\n\\n    def setUp(self):\\\n        self.project_dir = '/fake/project/dir'\\\n        self.manager = ProjectMetadataManager(self.project_dir)\\\\\n\\n    @patch('os.path.exists') \\\n    @patch('builtins.open', new_callable=mock_open, read_data='{\"project_name\": \"Test Project\"}') \\\n    def test_load_metadata(self, mock_file, mock_exists):\\\n        mock_exists.return_value = True\\\n        metadata = self.manager.load_metadata()\\\n        self.assertEqual(metadata['project_name'], 'Test Project')\\\\\n        mock_file.assert_called_once_with(os.path.join(self.project_dir, 'drd.json'), 'r')\\\\\n\\n    @patch('json.dump') \\\n    @patch('builtins.open', new_callable=mock_open) \\\n    def test_save_metadata(self, mock_file, mock_json_dump):\\\n        self.manager.save_metadata()\\\n        mock_file.assert_called_once_with(os.path.join(self.project_dir, 'drd.json'), 'w')\\\\\n        mock_json_dump.assert_called_once()\\\\\n\\n    @patch.object(ProjectMetadataManager, 'save_metadata') \\\n    def test_update_file_metadata(self, mock_save):\\\n        self.manager.update_file_metadata('test.py', 'python', 'print(\\"Hello\\")\\'', 'A test Python file')\\\\\n        mock_save.assert_called_once()\\\n        file_entry = next((f for f in self.manager.metadata['files'] if f['filename'] == 'test.py'), None)\\\\\n        self.assertIsNotNone(file_entry)\\\\\n        self.assertEqual(file_entry['type'], 'python')\\\\\n        self.assertEqual(file_entry['content_preview'], 'print(\\"Hello\\")\\')\\\\\n        self.assertEqual(file_entry['description'], 'A test Python file')\\\\\n\\n    def test_get_project_context(self):\\\n        self.manager.metadata = {\\\\\