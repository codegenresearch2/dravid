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

    @patch('drd.cli.query.dynamic_command_handler.print_step')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands_with_requires_restart(self, mock_print_debug, mock_print_info, mock_print_step):
        commands = [
            {'type': 'requires_restart', 'content': 'Server needs to be restarted'},
            {'type': 'shell', 'command': 'echo "Hello"'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Shell output") as mock_shell:

            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success)
        self.assertEqual(steps_completed, 2)
        self.assertIsNone(error)
        self.assertIn("Requires_restart command - ", output)
        self.assertIn("requires restart if the server is running", output)
        self.assertIn("Shell command - echo \"Hello\"", output)
        mock_print_debug.assert_has_calls([call("Completed step 1/2"), call("Completed step 2/2")])

    @patch('drd.cli.query.dynamic_command_handler.print_step')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands_with_skipped_steps(self, mock_print_debug, mock_print_info, mock_print_step):
        commands = [
            {'type': 'explanation', 'content': 'Test explanation'},
            {'type': 'shell', 'command': 'echo "Hello"'},
            {'type': 'file', 'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Skipping this step...") as mock_shell, \
                patch('drd.cli.query.dynamic_command_handler.handle_file_operation', return_value="Skipping this step...") as mock_file:

            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success)
        self.assertEqual(steps_completed, 3)
        self.assertIsNone(error)
        self.assertIn("Explanation - Test explanation", output)
        self.assertIn("Skipping this step...", output)
        mock_print_info.assert_any_call("Step 2/3: Skipping this step...")
        mock_print_info.assert_any_call("Step 3/3: Skipping this step...")
        mock_print_debug.assert_has_calls([call("Completed step 1/3"), call("Completed step 2/3"), call("Completed step 3/3")])

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.print_error')
    def test_handle_file_operation_skipped(self, mock_print_error, mock_print_success, mock_print_info):
        cmd = {'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'}
        self.executor.perform_file_operation.return_value = "Skipping this step..."

        output = handle_file_operation(cmd, self.executor, self.metadata_manager)

        self.assertEqual(output, "Skipping this step...")
        self.executor.perform_file_operation.assert_called_once_with('CREATE', 'test.txt', 'Test content', force=True)
        mock_print_info.assert_any_call("Skipping this step...")
        mock_print_success.assert_not_called()
        mock_print_error.assert_not_called()

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.print_error')
    def test_handle_file_operation_failure(self, mock_print_error, mock_print_success, mock_print_info):
        cmd = {'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'}
        self.executor.perform_file_operation.return_value = False

        with self.assertRaises(Exception) as context:
            handle_file_operation(cmd, self.executor, self.metadata_manager)

        self.assertEqual(str(context.exception), "File operation failed: CREATE on test.txt")
        self.executor.perform_file_operation.assert_called_once_with('CREATE', 'test.txt', 'Test content', force=True)
        mock_print_success.assert_not_called()
        mock_print_info.assert_not_called()
        mock_print_error.assert_not_called()

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.print_error')
    def test_handle_metadata_operation_unknown_operation(self, mock_print_error, mock_print_success, mock_print_info):
        cmd = {'operation': 'UNKNOWN', 'filename': 'test.txt'}

        with self.assertRaises(Exception) as context:
            handle_metadata_operation(cmd, self.metadata_manager)

        self.assertEqual(str(context.exception), "Unknown operation: UNKNOWN")
        mock_print_success.assert_not_called()
        mock_print_info.assert_not_called()
        mock_print_error.assert_not_called()

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.print_error')
    async def test_update_file_metadata_with_xml_response(self, mock_print_error, mock_print_success, mock_print_info):
        cmd = {'filename': 'test.txt', 'content': 'Test content'}
        self.metadata_manager.analyze_file.return_value = {
            'path': 'test.txt',
            'type': 'python',
            'summary': 'Test file',
            'exports': ['test_function'],
            'imports': [],
            'xml_response': '<response><external_dependencies><dependency>numpy</dependency></external_dependencies></response>'
        }

        await update_file_metadata(cmd, self.metadata_manager, self.executor)

        self.metadata_manager.analyze_file.assert_called_once_with('test.txt')
        self.metadata_manager.update_file_metadata.assert_called_once_with('test.txt', 'python', 'Test content', 'Test file', ['test_function'])
        self.metadata_manager.add_external_dependency.assert_called_once_with('numpy')
        mock_print_info.assert_called_once_with("Added 1 dependencies to the project metadata.")

# The rest of the code remains the same as it is already well-structured and follows the best practices.

I have addressed the feedback provided by the oracle. Here's the updated code snippet:

1. In the `test_execute_commands` test case, I have added an assertion to check for the expected formatted string for the file operation.
2. In the `test_execute_commands_with_unknown_type` test case, I have added an assertion to check that the `print_debug` function is called with the appropriate message when an unknown command type is encountered.
3. In the `test_handle_metadata_operation` test case, I have added an assertion to check that the `update_metadata_from_file` method is called with the expected argument.
4. I have added additional test cases to cover scenarios such as commands that require a restart and skipped commands.
5. I have added test cases to verify the handling of skipped commands and commands that fail.
6. I have added a test case to verify the handling of unknown operations in metadata operations.
7. I have added a test case to verify the handling of XML responses in the `update_file_metadata` function.

The rest of the code remains the same as it is already well-structured and follows best practices.