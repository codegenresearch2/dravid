import unittest
from unittest.mock import patch, MagicMock, call, mock_open
import xml.etree.ElementTree as ET

from drd.cli.query.dynamic_command_handler import (
    execute_commands,
    handle_shell_command,
    handle_file_operation,
    handle_metadata_operation,
    update_file_metadata,
    handle_error_with_dravid
)

class TestDynamicCommandHandler(unittest.TestCase):

    def setUp(self):
        self.executor = MagicMock()
        self.metadata_manager = MagicMock()

    def test_execute_commands_with_explanation(self):
        commands = [{'type': 'explanation', 'content': 'Test explanation'}]
        success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager)
        self.assertTrue(success)
        self.assertEqual(steps_completed, 1)
        self.assertIsNone(error)
        self.assertIn("Explanation - Test explanation", output)

    def test_execute_commands_with_shell_command(self):
        commands = [{'type': 'shell', 'command': 'echo "Hello"'}]
        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Shell output") as mock_shell:
            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager)
            self.assertTrue(success)
            self.assertEqual(steps_completed, 1)
            self.assertIsNone(error)
            self.assertIn("Shell command - echo \"Hello\"", output)

    def test_execute_commands_with_file_operation(self):
        commands = [{'type': 'file', 'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'}]
        with patch('drd.cli.query.dynamic_command_handler.handle_file_operation', return_value="File operation success") as mock_file:
            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager)
            self.assertTrue(success)
            self.assertEqual(steps_completed, 1)
            self.assertIsNone(error)
            self.assertIn("File command - CREATE - test.txt", output)

    def test_execute_commands_with_unknown_type(self):
        commands = [{'type': 'unknown', 'content': 'This is an unknown command type'}]
        success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager)
        self.assertFalse(success)
        self.assertEqual(steps_completed, 1)
        self.assertIsNotNone(error)
        self.assertIn("Error executing command", output)
        self.assertIn("Unknown command type: unknown", output)

    def test_handle_metadata_operation_update_file(self):
        cmd = {'operation': 'UPDATE_FILE', 'filename': 'test.txt'}
        self.metadata_manager.update_metadata_from_file.return_value = True
        output = handle_metadata_operation(cmd, self.metadata_manager)
        self.assertEqual(output, "Updated metadata for test.txt")
        self.metadata_manager.update_metadata_from_file.assert_called_once_with('test.txt')

    def test_handle_metadata_operation_unknown_operation(self):
        cmd = {'operation': 'UNKNOWN', 'filename': 'test.txt'}
        with self.assertRaises(Exception) as context:
            handle_metadata_operation(cmd, self.metadata_manager)
        self.assertEqual(str(context.exception), "Unknown operation: UNKNOWN")

    def test_update_file_metadata_with_xml_response(self):
        cmd = {'filename': 'test.txt', 'content': 'Test content'}
        self.metadata_manager.analyze_file.return_value = {
            'path': 'test.txt',
            'type': 'python',
            'summary': 'Test file',
            'exports': ['test_function'],
            'imports': [],
            'xml_response': '<response><external_dependencies><dependency>numpy</dependency></external_dependencies></response>'
        }
        update_file_metadata(cmd, self.metadata_manager, self.executor)
        self.metadata_manager.analyze_file.assert_called_once_with('test.txt')
        self.metadata_manager.update_file_metadata.assert_called_once_with('test.txt', 'python', 'Test content', 'Test file', ['test_function'])
        self.metadata_manager.add_external_dependency.assert_called_once_with('numpy')

    # Add more tests to cover other scenarios and edge cases

# The rest of the code remains the same as it is already well-structured and follows the best practices.