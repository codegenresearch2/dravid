import unittest
from unittest.mock import patch, MagicMock, call, mock_open
import xml.etree.ElementTree as ET
import os

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
        self.safe_directories = ['/safe/dir1', '/safe/dir2']

    def tearDown(self):
        self.executor.reset_directory()

    @patch('drd.cli.query.dynamic_command_handler.print_step')
    @patch('drd.cli.query.dynamic_command_handler.print_info')
    @patch('drd.cli.query.dynamic_command_handler.print_debug')
    def test_execute_commands(self, mock_print_debug, mock_print_info, mock_print_step):
        commands = [
            {'type': 'explanation', 'content': 'Test explanation'},
            {'type': 'shell', 'command': 'echo "Hello"'},
            {'type': 'file', 'operation': 'CREATE',
             'filename': 'test.txt', 'content': 'Test content'},
        ]

        with patch('drd.cli.query.dynamic_command_handler.handle_shell_command', return_value="Shell output") as mock_shell, \
             patch('drd.cli.query.dynamic_command_handler.handle_file_operation', return_value="File operation success") as mock_file, \
             patch('drd.cli.query.dynamic_command_handler.handle_metadata_operation', return_value="Metadata operation success") as mock_metadata:

            success, steps_completed, error, output = execute_commands(
                commands, self.executor, self.metadata_manager, debug=True)

        self.assertTrue(success)
        self.assertEqual(steps_completed, 3)
        self.assertIsNone(error)
        self.assertIn("Explanation - Test explanation", output)
        self.assertIn("Shell command - echo \"Hello\"", output)
        self.assertIn("File command - CREATE - test.txt", output)
        mock_print_debug.assert_called_with("Completed step 3/3")

    # Rest of the tests...

    @patch('os.chdir')
    @patch('os.path.abspath')
    def test_handle_cd_command(self, mock_abspath, mock_chdir):
        mock_abspath.return_value = '/safe/dir/app'
        result = self.executor._handle_cd_command('cd app')
        self.assertEqual(result, "Changed directory to: /safe/dir/app")
        mock_chdir.assert_called_once_with('/safe/dir/app')
        self.assertEqual(self.executor.current_dir, '/safe/dir/app')

    @patch('subprocess.Popen')
    def test_execute_single_command(self, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.readline.return_value = 'output line'
        mock_process.communicate.return_value = ('', '')
        mock_popen.return_value = mock_process

        result = self.executor._execute_single_command('echo "Hello"', 300)
        self.assertEqual(result, 'output line')
        mock_popen.assert_called_once_with(
            'echo "Hello"',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.executor.env,
            cwd=self.executor.current_dir
        )

    # Rest of the tests...

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('click.confirm')
    def test_perform_file_operation_create(self, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = False
        mock_confirm.return_value = True
        filename = os.path.join(self.safe_directories[0], 'test.txt')
        result = self.executor.perform_file_operation('CREATE', filename, 'content')
        self.assertTrue(result)
        mock_file.assert_called_with(filename, 'w')
        mock_file().write.assert_called_with('content')

    # Rest of the tests...

    @patch('os.chdir')
    def test_reset_directory(self, mock_chdir):
        self.executor.current_dir = '/safe/dir/app'
        self.executor.reset_directory()
        mock_chdir.assert_called_once_with(self.executor.initial_dir)
        self.assertEqual(self.executor.current_dir, self.executor.initial_dir)

# Rest of the code...