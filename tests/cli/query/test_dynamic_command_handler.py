import unittest
from unittest.mock import patch, MagicMock

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

    @patch('drd.cli.query.dynamic_command_handler.handle_shell_command')
    @patch('drd.cli.query.dynamic_command_handler.handle_file_operation')
    @patch('drd.cli.query.dynamic_command_handler.handle_metadata_operation')
    @patch('drd.cli.query.dynamic_command_handler.print_step')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands(self, mock_print_debug, mock_print_info, mock_print_step,
                               mock_handle_metadata, mock_handle_file, mock_handle_shell):
        commands = [
            {'type': 'explanation', 'content': 'Test explanation'},
            {'type': 'shell', 'command': 'echo "Hello"'},
            {'type': 'file', 'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.Executor') as mock_executor,
             patch('drd.cli.query.dynamic_command_handler.ProjectMetadataManager') as mock_metadata_manager:

            success, steps_completed, error, output = execute_commands(
                commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success)
        self.assertEqual(steps_completed, 3)
        self.assertIsNone(error)
        self.assertIn('Explanation - Test explanation', output)
        self.assertIn('Shell command - echo "Hello"', output)
        self.assertIn('File command - CREATE - test.txt', output)
        mock_print_debug.assert_called_with('Completed step 3/3')

    @patch('drd.cli.query.dynamic_command_handler.print_info') as mock_print_info,
         patch('drd.cli.query.dynamic_command_handler.print_success') as mock_print_success,
         patch('drd.cli.query.dynamic_command_handler.click.echo') as mock_echo:

        @patch('drd.cli.query.dynamic_command_handler.handle_shell_command')  # Correctly formatted @patch decorator
        def test_handle_shell_command(self, mock_handle_shell, mock_echo, mock_print_success, mock_print_info):
            cmd = {'command': 'echo "Hello"'}
            self.executor.execute_shell_command.return_value = 'Hello'

            output = handle_shell_command(cmd, self.executor)

            self.assertEqual(output, 'Hello')
            self.executor.execute_shell_command.assert_called_once_with('echo "Hello"')
            mock_print_success.assert_called_once_with('Successfully executed: echo "Hello"')
            mock_echo.assert_called_once_with('Command output:
Hello')

    @patch('drd.cli.query.dynamic_command_handler.print_info') as mock_print_info,
         patch('drd.cli.query.dynamic_command_handler.print_success') as mock_print_success,
         patch('drd.cli.query.dynamic_command_handler.update_file_metadata') as mock_update_metadata:

        @patch('drd.cli.query.dynamic_command_handler.handle_file_operation')  # Correctly formatted @patch decorator
        def test_handle_file_operation(self, mock_update_metadata, mock_handle_file, mock_print_success, mock_print_info):
            cmd = {'operation': 'CREATE', 'filename': 'test.txt', 'content': 'Test content'}
            self.executor.perform_file_operation.return_value = True

            output = handle_file_operation(cmd, self.executor, self.metadata_manager)

            self.assertEqual(output, 'Success')
            self.executor.perform_file_operation.assert_called_once_with('CREATE', 'test.txt', 'Test content', force=True)
            mock_update_metadata.assert_called_once_with(cmd, self.metadata_manager, self.executor)

    @patch('drd.cli.query.dynamic_command_handler.generate_file_description') as mock_generate_description:

        async def test_update_file_metadata(self, mock_generate_description):
            cmd = {'filename': 'test.txt', 'content': 'Test content'}
            mock_generate_description.return_value = ('python', 'Test file', ['test_function'])

            await update_file_metadata(cmd, self.metadata_manager, self.executor)

            self.metadata_manager.get_project_context.assert_called_once()
            self.executor.get_folder_structure.assert_called_once()
            mock_generate_description.assert_called_once_with('test.txt', 'Test content', self.metadata_manager.get_project_context(), self.executor.get_folder_structure())
            self.metadata_manager.update_file_metadata.assert_called_once_with('test.txt', 'python', 'Test content', 'Test file', ['test_function'])

    @patch('drd.cli.query.dynamic_command_handler.print_error') as mock_print_error,
         patch('drd.cli.query.dynamic_command_handler.print_info') as mock_print_info,
         patch('drd.cli.query.dynamic_command_handler.print_success') as mock_print_success,
         patch('drd.cli.query.dynamic_command_handler.call_dravid_api') as mock_call_api,
         patch('drd.cli.query.dynamic_command_handler.execute_commands') as mock_execute_commands,
         patch('drd.cli.query.dynamic_command_handler.click.echo') as mock_echo:

        @patch('drd.cli.query.dynamic_command_handler.handle_error_with_dravid')  # Correctly formatted @patch decorator
        def test_handle_error_with_dravid(self, mock_echo, mock_execute_commands, mock_call_api, mock_print_success, mock_print_info, mock_print_error):
            error = Exception('Test error')
            cmd = {'type': 'shell', 'command': 'echo "Hello"'}

            mock_call_api.return_value = [{'type': 'shell', 'command': "echo 'Fixed'"}]
            mock_execute_commands.return_value = (True, 1, None, 'Fix applied')

            result = handle_error_with_dravid(error, cmd, self.executor, self.metadata_manager)

            self.assertTrue(result)
            mock_call_api.assert_called_once()
            mock_execute_commands.assert_called_once()
            mock_print_success.assert_called_with('All fix steps successfully applied.')
