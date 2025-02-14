import unittest
from unittest.mock import patch, MagicMock, call, mock_open
import xml.etree.ElementTree as ET
from drd.cli.query.dynamic_command_handler import (
    execute_commands,
    handle_shell_command,
    handle_file_operation,
    handle_metadata_operation,
    update_file_metadata,
    handle_error_with_dravid,
    handle_dependencies,
    update_project_info,
    update_dev_server_info
)

class TestDynamicCommandHandler(unittest.TestCase):

    def setUp(self):
        self.executor = MagicMock()
        self.metadata_manager = MagicMock()

    # Other test cases...

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.update_file_metadata')
    def test_handle_file_operation(self, mock_update_metadata, mock_print_success, mock_print_info):
        cmd = {'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'}
        self.executor.perform_file_operation.return_value = True

        output = handle_file_operation(cmd, self.executor, self.metadata_manager)

        self.assertEqual(output, "Success")
        self.executor.perform_file_operation.assert_called_once_with(
            'CREATE', 'test.txt', 'Test content', force=True)
        mock_update_metadata.assert_called_once_with(cmd, self.metadata_manager, self.executor)

    @patch('drd.cli.query.dynamic_command_handler.generate_file_description')
    @patch('drd.cli.query.dynamic_command_handler.handle_dependencies')
    def test_update_file_metadata(self, mock_handle_dependencies, mock_generate_description):
        cmd = {'filename': 'test.txt', 'content': 'Test content'}
        mock_generate_description.return_value = {
            'path': 'test.txt',
            'type': 'python',
            'summary': 'Test file',
            'exports': ['test_function'],
            'imports': [],
            'xml_response': '<root><external_dependencies><dependency>dep1</dependency></external_dependencies></root>'
        }

        update_file_metadata(cmd, self.metadata_manager, self.executor)

        self.metadata_manager.update_file_metadata.assert_called_once_with(
            'test.txt', 'python', 'Test content', 'Test file', ['test_function'], [])
        mock_handle_dependencies.assert_called_once_with({'path': 'test.txt', 'xml_response': '<root><external_dependencies><dependency>dep1</dependency></external_dependencies></root>'}, self.metadata_manager)

    @patch('drd.cli.query.dynamic_command_handler.print_error')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    def test_handle_dependencies(self, mock_print_info, mock_print_error):
        file_info = {'xml_response': '<root><external_dependencies><dependency>dep1</dependency><dependency>dep2</dependency></external_dependencies></root>'}
        metadata_manager = MagicMock()

        handle_dependencies(file_info, metadata_manager)

        metadata_manager.add_external_dependency.assert_any_call('dep1')
        metadata_manager.add_external_dependency.assert_any_call('dep2')
        mock_print_info.assert_called_once_with("Added 2 dependencies to the project metadata.")

    @patch('drd.cli.query.dynamic_command_handler.print_error')
    def test_handle_dependencies_xml_error(self, mock_print_error):
        file_info = {'xml_response': 'invalid xml'}
        metadata_manager = MagicMock()

        handle_dependencies(file_info, metadata_manager)

        mock_print_error.assert_called_once_with("Failed to parse XML response for dependencies")

    # Other test cases...