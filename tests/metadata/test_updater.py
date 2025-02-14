import unittest\\nfrom unittest.mock import patch, MagicMock, mock_open\\\\\nimport xml.etree.ElementTree as ET\\\\\\nfrom drd.metadata.updater import update_metadata_with_dravid\\\\\nimport asyncio\\\\\n\\\\\nclass TestMetadataUpdater(unittest.TestCase):\\\\\n    def setUp(self):\\\\\n        self.current_dir = '/fake/project/dir'\\\\\n        self.meta_description = "Update project metadata"\\\\\n        self.project_context = "This is a sample project context"\\\\\n        self.folder_structure = {\\\n            'src': {\\\n                'main.py': 'file',\\\\\n                'utils.py': 'file'\\\\\n            },\\\\\n            'tests': {\\\n                'test_main.py': 'file'\\\\\n            },\\\\\n            'README.md': 'file',\\\\\n            'package.json': 'file'\\\\\n        }\\\\\n\\\\\n    @patch('drd.metadata.updater.ProjectMetadataManager') \\\\\n    @patch('drd.metadata.updater.get_ignore_patterns') \\\\\n    @patch('drd.metadata.updater.get_folder_structure') \\\\\n    @patch('drd.metadata.updater.call_dravid_api_with_pagination') \\\\\n    @patch('drd.metadata.updater.extract_and_parse_xml') \\\\\n    @patch('drd.metadata.updater.find_file_with_dravid') \\\\\n    @patch('drd.metadata.updater.print_info') \\\\\n    @patch('drd.metadata.updater.print_success') \\\\\n    @patch('drd.metadata.updater.print_warning') \\\\\n    @patch('drd.metadata.updater.print_error') \\\\\n    def test_update_metadata_with_dravid(self, mock_print_error, mock_print_warning, \\\\\n                                         mock_print_success, mock_print_info, \\\\\n                                         mock_find_file, mock_extract_xml, mock_call_api, \\\\\n                                         mock_get_folder_structure, mock_get_ignore_patterns, \\\\\n                                         mock_metadata_manager): \\\\\n        # Set up mocks \\\\\n        mock_metadata_manager.return_value.get_project_context.return_value = self.project_context \\\\\n        mock_get_ignore_patterns.return_value = ([], "No ignore patterns found") \\\\\n        mock_get_folder_structure.return_value = self.folder_structure \\\\\n\\\\\n        mock_call_api.return_value = """ \\\\\n        <response> \\\\\n            <files> \\\\\n                <file> \\\\\n                    <path>src/main.py</path> \\\\\n                    <action>update</action> \\\\\n                    <metadata> \\\\\n                        <type>python</type> \\\\\n                        <description>Main Python file</description> \\\\\n                        <exports>main_function</exports> \\\\\n                        <imports>os</imports> \\\\\n                        <external_dependencies> \\\\\n                            <dependency>requests==2.26.0</dependency> \\\\\n                        </external_dependencies> \\\\\n                    </metadata> \\\\\n                </file> \\\\\n                <file> \\\\\n                    <path>README.md</path> \\\\\n                    <action>remove</action> \\\\\n                </file> \\\\\n                <file> \\\\\n                    <path>package.json</path> \\\\\n                    <action>update</action> \\\\\n                    <metadata> \\\\\n                        <type>json</type> \\\\\n                        <description>Package configuration file</description> \\\\\n                        <exports>None</exports> \\\\\n                        <imports>None</imports> \\\\\n                        <external_dependencies> \\\\\n                            <dependency>react@^17.0.2</dependency> \\\\\n                            <dependency>jest@^27.0.6</dependency> \\\\\n                        </external_dependencies> \\\\\n                    </metadata> \\\\\n                </file> \\\\\n            </files> \\\\\n        </response> \""" \\\\\n        mock_root = ET.fromstring(mock_call_api.return_value) \\\\\n        mock_extract_xml.return_value = mock_root \\\\\n\\\\\n        mock_find_file.side_effect = [ \\\\\n            '/fake/project/dir/src/main.py', '/fake/project/dir/package.json' \\\\\n        ] \\\\\n\\\\\n        # Mock file contents \\\\\n        mock_file_contents = { \\\\\n            '/fake/project/dir/src/main.py': "print('Hello, World!')", \\\\\n            '/fake/project/dir/package.json': '{\"name\": \"test-project\"}' \\\\\n        } \\\\\n\\\\\n        def mock_open_file(filename, *args, **kwargs): \\\\\n            return mock_open(read_data=mock_file_contents.get(filename, ""))() \\\\\n\\\\\n        with patch('builtins.open', mock_open_file): \\\\\n            # Call the function \\\\\n            update_metadata_with_dravid( \\\\\n                self.meta_description, self.current_dir) \\\\\n\\\\\n        # Assertions \\\\\n        mock_metadata_manager.assert_called_once_with(self.current_dir) \\\\\n        mock_get_ignore_patterns.assert_called_once_with(self.current_dir) \\\\\n        mock_get_folder_structure.assert_called_once_with(self.current_dir, []) \\\\\n        mock_call_api.assert_called_once() \\\\\n        mock_extract_xml.assert_called_once_with(mock_call_api.return_value) \\\\\n\\\\\n        # Check if metadata was correctly updated and removed \\\\\n        mock_metadata_manager.return_value.update_file_metadata.assert_any_call( \\\\\n            '/fake/project/dir/src/main.py', 'python', "print('Hello, World!')", 'Main Python file', [ \\\\\n                'main_function' \\\\\n            ], ['os'] \\\\\n        ) \\\\\n        mock_metadata_manager.return_value.update_file_metadata.assert_any_call( \\\\\n            '/fake/project/dir/package.json', 'json', '{\"name\": \"test-project\"}', 'Package configuration file', [ \\\\\n            ], [] \\\\\n        ) \\\\\n        mock_metadata_manager.return_value.remove_file_metadata.assert_called_once_with( \\\\\n            'README.md') \\\\\n\\\\\n        # Check if external dependencies were added \\\\\n        mock_metadata_manager.return_value.add_external_dependency.assert_any_call( \\\\\n            'requests==2.26.0') \\\\\n        mock_metadata_manager.return_value.add_external_dependency.assert_any_call( \\\\\n            'react@^17.0.2') \\\\\n        mock_metadata_manager.return_value.add_external_dependency.assert_any_call( \\\\\n            'jest@^27.0.6') \\\\\n\\\\\n        # Check if appropriate messages were printed \\\\\n        mock_print_info.assert_any_call( \\\\\n            "Updating metadata based on the provided description...") \\\\\n        mock_print_success.assert_any_call( \\\\\n            "Updated metadata for file: /fake/project/dir/src/main.py") \\\\\n        mock_print_success.assert_any_call( \\\\\n            "Updated metadata for file: /fake/project/dir/package.json") \\\\\n        mock_print_success.assert_any_call( \\\\\n            "Removed metadata for file: README.md") \\\\\n        mock_print_success.assert_any_call("Metadata update completed.") \\\\\n\\\\\nif __name__ == '__main__': \\\\\n    unittest.main() \\\\\n"\\"}