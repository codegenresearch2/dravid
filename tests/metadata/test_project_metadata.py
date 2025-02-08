import unittest\\"\\\nfrom unittest.mock import patch, mock_open, MagicMock\\"\\\nimport os\\"\\\nimport sys\\"\\\nimport json\\"\\\nfrom datetime import datetime\\"\\\nimport xml.etree.ElementTree as ET\\"\\\n\\"\\\nfrom src.drd.metadata.project_metadata import ProjectMetadataManager\\"\\\n\\"\\\nclass TestProjectMetadataManager(unittest.TestCase):\\"\\\n    def setUp(self):\\"\\\n        self.project_dir = '/fake/project/dir'\\"\\\n        self.manager = ProjectMetadataManager(self.project_dir)\\"\\\n\\"\\\n    @patch('os.walk')\\"\\\n    def test_get_ignore_patterns(self, mock_walk):\\"\\\n        mock_walk.return_value = [\\"\\\n            ('/fake/project/dir', [], ['.gitignore']),\\"\\\n            ('/fake/project/dir/subfolder', [], ['.gitignore'])\"\\\n        ]\\"\\\n        mock_open_calls = [\\"\\\n            mock_open(read_data='*.log\nnode_modules/').return_value,\\"\\\n            mock_open(read_data='*.tmp\n').return_value\"\\\n        ]\\"\\\n        with patch('builtins.open', side_effect=mock_open_calls):\\"\\\n            patterns = self.manager.get_ignore_patterns()\\"\\\n\\"\\\n        self.assertIn('*.log', patterns) \\"\\\n        self.assertIn('node_modules/', patterns) \\"\\\n        self.assertIn('subfolder/*.tmp', patterns) \\"\\\n\\"\\\n    def test_should_ignore(self):\\"\\\n        self.manager.ignore_patterns = [\\"\\\n            '*.log', 'node_modules/', 'subfolder/*.tmp']\\"\\\n        self.assertTrue(self.manager.should_ignore( \\"\\\n            '/fake/project/dir/test.log'))\\"\\\n        self.assertTrue(self.manager.should_ignore( \\"\\\n            '/fake/project/dir/node_modules/package.json'))\\"\\\n        self.assertTrue(self.manager.should_ignore( \\"\\\n            '/fake/project/dir/node_modules/subfolder/file.js'))\\"\\\n        self.assertTrue(self.manager.should_ignore( \\"\\\n            '/fake/project/dir/subfolder/test.tmp'))\\"\\\n        self.assertFalse(self.manager.should_ignore( \\"\\\n            '/fake/project/dir/src/main.py'))\\"\\\n        self.assertFalse(self.manager.should_ignore( \\"\\\n            '/fake/project/dir/package.json'))\\"\\\n\\"\\\n    @patch('os.walk')\\"\\\n    def test_get_directory_structure(self, mock_walk):\\"\\\n        mock_walk.return_value = [\\"\\\n            ('/fake/project/dir', ['src'], ['README.md']),\\"\\\n            ('/fake/project/dir/src', [], ['main.py', 'utils.py'])\"\\\n        ]\\"\\\n        structure = self.manager.get_directory_structure(self.project_dir) \\"\\\n        expected_structure = { \\"\\\n            'files': ['README.md'], \\"\\\n            'directories': ['src'], \\"\\\n            'src': { \\"\\\n                'files': ['main.py', 'utils.py'] \\"\\\n            } \\"\\\n        } \\"\\\n        self.assertEqual(structure, expected_structure)\\"\\\n\\"\\\n    def test_is_binary_file(self):\\"\\\n        self.assertTrue(self.manager.is_binary_file('test.exe'))\\"\\\n        self.assertTrue(self.manager.is_binary_file('image.png'))\\"\\\n        self.assertFalse(self.manager.is_binary_file('script.py'))\\"\\\n        self.assertFalse(self.manager.is_binary_file('config.json'))\\"\\\n\\"\\\n    @patch('src.drd.metadata.project_metadata.call_dravid_api_with_pagination') \\"\\\n    @patch('builtins.open', new_callable=mock_open, read_data='print("Hello, World!")') \\"\\\n    async def test_analyze_file(self, mock_file, mock_api_call): \\"\\\n        mock_api_call.return_value = ''' \\"\\\n        <response> \\"\\\n          <metadata> \\"\\\n            <type>python</type> \\"\\\n            <description>A simple Python script</description> \\"\\\n            <exports>None</exports> \\"\\\n            <imports>None</imports> \\"\\\n          </metadata> \\"\\\n        </response> ''' \\"\\\n        file_info = await self.manager.analyze_file('/fake/project/dir/script.py') \\"\\\n        self.assertEqual(file_info['path'], 'script.py') \\"\\\n        self.assertEqual(file_info['type'], 'python') \\"\\\n        self.assertEqual(file_info['summary'], 'A simple Python script') \\"\\\n\\"\\\n    @patch('src.drd.metadata.project_metadata.ProjectMetadataManager.analyze_file') \\"\\\n    @patch('os.walk') \\"\\\n    async def test_build_metadata(self, mock_walk, mock_analyze_file): \\"\\\n        mock_walk.return_value = [ \\"\\\n            ('/fake/project/dir', [], ['main.py', 'README.md'])\"\\\n        ]\\"\\\n        mock_analyze_file.side_effect = [ \\"\\\n            { \\"\\\n                'path': 'main.py', \\"\\\n                'type': 'python', \\"\\\n                'summary': 'Main Python script', \\"\\\n                'exports': ['main_function'], \\"\\\n                'imports': ['os'] \\"\\\n            }, \\"\\\n            None  # Simulating skipping README.md \\"\\\n        ]\\"\\\n        loader = MagicMock() \\"\\\n        metadata = await self.manager.build_metadata(loader) \\"\\\n\\"\\\n        self.assertEqual(metadata['environment']['primary_language'], 'python') \\"\\\n        self.assertEqual(len(metadata['key_files']), 1) \\"\\\n        self.assertEqual(metadata['key_files'][0]['path'], 'main.py') \\"\\\n