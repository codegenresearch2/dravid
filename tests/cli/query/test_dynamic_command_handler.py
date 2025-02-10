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

    @patch('drd.cli.query.dynamic_command_handler.print_step')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands(self, mock_print_debug, mock_print_info, mock_print_step):
        commands = [
            {'type': 'explanation', 'content': 'Test explanation'},
            {'type': 'shell', 'command': 'echo "Hello"'},
            {'type': 'file', 'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Shell output") as mock_shell, \
                patch('drd.cli.query.dynamic_command_handler.handle_file_operation', return_value="File operation success") as mock_file, \
                patch('drd.cli.query.dynamic_command_handler.handle_metadata_operation', return_value="Metadata operation success") as mock_metadata:

            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success)
        self.assertEqual(steps_completed, 3)
        self.assertIsNone(error)
        self.assertIn("Explanation - Test explanation", output)
        self.assertIn("Shell command - echo \"Hello\"", output)
        self.assertIn("File command - CREATE - test.txt", output)
        mock_print_debug.assert_called_with("Completed step 3/3")

    @patch('drd.cli.query.dynamic_command_handler.print_step')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands_with_unknown_type(self, mock_print_debug, mock_print_info, mock_print_step):
        commands = [
            {'type': 'unknown', 'content': 'This is an unknown command type'},
        ]

        success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager, debug=True)

        self.assertFalse(success)
        self.assertEqual(steps_completed, 1)
        self.assertIsNotNone(error)
        self.assertIn("Error executing command", output)
        self.assertIn("Unknown command type: unknown", output)
        mock_print_debug.assert_called_once_with("Completed step 1/1")

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.print_error')
    def test_handle_metadata_operation(self, mock_print_error, mock_print_success, mock_print_info):
        cmd = {'operation': 'UPDATE_FILE', 'filename': 'test.txt'}
        self.metadata_manager.update_metadata_from_file.return_value = True

        output = handle_metadata_operation(cmd, self.metadata_manager)

        self.assertEqual(output, "Updated metadata for test.txt")
        self.metadata_manager.update_metadata_from_file.assert_called_once_with('test.txt')
        mock_print_success.assert_called_once_with("Updated metadata for file: test.txt")
        mock_print_info.assert_not_called()
        mock_print_error.assert_not_called()

    # Add more tests to cover other scenarios and edge cases

# The rest of the code remains the same as it is already well-structured and follows the best practices.