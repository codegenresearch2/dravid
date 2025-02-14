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

    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands(self, mock_print_debug):
        commands = [
            {'type': 'explanation', 'content': 'Test explanation'},
            {'type': 'shell', 'command': 'echo "Hello"'},
            {'type': 'file', 'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Shell output") as mock_shell, \
                patch('drd.cli.query.dynamic_command_handler.handle_file_operation', return_value="File operation success") as mock_file, \
                patch('drd.cli.query.dynamic_command_handler.handle_metadata_operation', return_value="Metadata operation success") as mock_metadata:

            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success, "All commands should be executed successfully")
        self.assertEqual(steps_completed, 3, "The number of steps completed should match the number of commands")
        self.assertIsNone(error, "No errors should occur during the execution")
        self.assertIn("Explanation - Test explanation", output, "The output should include the explanation")
        self.assertIn("Shell command - echo \"Hello\"", output, "The output should include the shell command")
        self.assertIn("File command - CREATE - test.txt", output, "The output should include the file command")
        mock_print_debug.assert_called_with("Completed step 3/3", "Debug message for completion of all steps should be printed")

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.click.echo')
    def test_handle_shell_command(self, mock_echo, mock_print_success, mock_print_info):
        cmd = {'command': 'echo "Hello"'}
        self.executor.execute_shell_command.return_value = "Hello"

        output = handle_shell_command(cmd, self.executor)

        self.assertEqual(output, "Hello", "The output of the shell command should be returned")
        mock_print_info.assert_called_once_with("Executing shell command: echo \"Hello\"", "Information about the shell command should be printed")
        mock_print_success.assert_called_once_with("Successfully executed: echo \"Hello\"", "Success message for the shell command should be printed")
        mock_echo.assert_called_once_with("Command output:\nHello", "The output of the shell command should be printed")

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.update_file_metadata')
    def test_handle_file_operation(self, mock_update_metadata, mock_print_success, mock_print_info):
        cmd = {'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'}
        self.executor.perform_file_operation.return_value = True

        output = handle_file_operation(cmd, self.executor, self.metadata_manager)

        self.assertEqual(output, "Success", "Success message should be returned")
        mock_print_success.assert_called_once_with("Successfully performed CREATE on file: test.txt", "Success message for the file operation should be printed")
        mock_update_metadata.assert_called_once_with(cmd, self.metadata_manager, self.executor, "Metadata for the file should be updated")

    @patch('drd.cli.query.dynamic_command_handler.generate_file_description')
    def test_update_file_metadata(self, mock_generate_description):
        cmd = {'filename': 'test.txt', 'content': 'Test content'}
        mock_generate_description.return_value = ('python', 'Test file', ['test_function'])

        update_file_metadata(cmd, self.metadata_manager, self.executor)

        mock_generate_description.assert_called_once_with('test.txt', 'Test content', self.metadata_manager.get_project_context(), self.executor.get_folder_structure(), "File description should be generated")
        self.metadata_manager.update_file_metadata.assert_called_once_with('test.txt', 'python', 'Test content', 'Test file', ['test_function'], "File metadata should be updated")

    @patch('drd.cli.query.dynamic_command_handler.print_error')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.call_dravid_api')
    @patch('drd.cli.query.dynamic_command_handler.execute_commands')
    @patch('drd.cli.query.dynamic_command_handler.click.echo')
    def test_handle_error_with_dravid(self, mock_echo, mock_execute_commands, mock_call_api, mock_print_success, mock_print_info, mock_print_error):
        error = Exception("Test error")
        cmd = {'type': 'shell', 'command': 'echo "Hello"'}

        mock_call_api.return_value = [{'type': 'shell', 'command': "echo 'Fixed'"}]
        mock_execute_commands.return_value = (True, 1, None, "Fix applied")

        result = handle_error_with_dravid(error, cmd, self.executor, self.metadata_manager)

        self.assertTrue(result, "The error should be handled successfully")
        mock_print_error.assert_called_once_with("Error executing command: Test error", "Error message should be printed")
        mock_print_info.assert_called_with("Sending error information to dravid for analysis...", "Information about sending error to dravid should be printed")
        mock_call_api.assert_called_once_with("Error query for dravid", include_context=True, "Dravid API should be called with error query")
        mock_execute_commands.assert_called_once_with(mock_call_api.return_value, self.executor, self.metadata_manager, is_fix=True, debug=False, "Fix commands should be executed")
        mock_print_success.assert_called_with("All fix steps successfully applied.", "Success message for fix application should be printed")

    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_success')
    @patch('drd.cli.query.dynamic_command_handler.click.echo')
    def test_handle_shell_command_skipped(self, mock_echo, mock_print_success, mock_print_info):
        cmd = {'command': 'echo "Hello"'}
        self.executor.execute_shell_command.return_value = "Skipping this step..."

        output = handle_shell_command(cmd, self.executor)

        self.assertEqual(output, "Skipping this step...", "The output of the skipped shell command should be returned")
        mock_print_info.assert_called_once_with("Skipping this step...", "Information about the skipped shell command should be printed")
        mock_print_success.assert_not_called()
        mock_echo.assert_not_called()

    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands_with_skipped_steps(self, mock_print_debug):
        commands = [
            {'type': 'explanation', 'content': 'Test explanation'},
            {'type': 'shell', 'command': 'echo "Hello"'},
            {'type': 'file', 'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Skipping this step...") as mock_shell, \
                patch('drd.cli.query.dynamic_command_handler.handle_file_operation', return_value="Skipping this step...") as mock_file:

            success, steps_completed, error, output = execute_commands(commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success, "All commands should be executed successfully, even if some are skipped")
        self.assertEqual(steps_completed, 3, "The number of steps completed should match the number of commands")
        self.assertIsNone(error, "No errors should occur during the execution, even if some commands are skipped")
        self.assertIn("Explanation - Test explanation", output, "The output should include the explanation")
        self.assertIn("Skipping this step...", output, "The output should include the skipped steps")
        mock_print_debug.assert_has_calls([call("Completed step 1/3"), call("Completed step 2/3"), call("Completed step 3/3")], "Debug messages for each completed step should be printed")