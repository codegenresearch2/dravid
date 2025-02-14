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
        self.initial_dir = '/initial/directory'
        os.chdir(self.initial_dir)
        self.executor.initial_dir = self.initial_dir
        self.executor.current_dir = self.initial_dir

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

    # Rest of the test methods remain the same

    @patch('os.chdir')
    def test_handle_cd_command(self, mock_chdir):
        result = self.executor._handle_cd_command('cd app')
        self.assertEqual(result, "Changed directory to: /initial/directory/app")
        mock_chdir.assert_called_once_with('/initial/directory/app')
        self.assertEqual(self.executor.current_dir, '/initial/directory/app')

    # Rest of the test methods remain the same

    def test_reset_directory(self):
        self.executor.current_dir = '/fake/path/app'
        self.executor.reset_directory()
        self.assertEqual(self.executor.current_dir, self.executor.initial_dir)
        self.assertEqual(os.getcwd(), self.executor.initial_dir)