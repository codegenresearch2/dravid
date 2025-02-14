import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import subprocess
import click
from colorama import Fore, Style
import time
import re
from drd.utils.print_utils import print_error, print_success, print_info, print_warning, create_confirmation_box
from drd.utils.diff import preview_file_changes
from drd.utils.apply_file_changes import apply_changes
from drd.metadata.common_utils import get_ignore_patterns, get_folder_structure

class TestExecutor(unittest.TestCase):
    @patch('os.chdir')
    def test_reset_directory(self, mock_chdir):
        self.executor.current_dir = '/fake/path/app'
        self.executor.reset_directory()
        mock_chdir.assert_called_once_with(self.executor.initial_dir)
        self.assertEqual(self.executor.current_dir, self.executor.initial_dir)

    @patch('click.confirm')
    @patch('os.chdir')
    @patch('os.path.abspath')
    def test_execute_shell_command_cd(self, mock_abspath, mock_chdir, mock_confirm):
        mock_confirm.return_value = True
        mock_abspath.return_value = '/fake/path/app'
        result = self.executor.execute_shell_command('cd app')
        self.assertEqual(result, "Changed directory to: /fake/path/app")
        mock_chdir.assert_called_once_with('/fake/path/app')
        self.assertEqual(self.executor.current_dir, '/fake/path/app')

    @patch('click.confirm')
    @patch('os.chdir')
    @patch('os.path.abspath')
    def test_execute_shell_command_cd_outside_allowed(self, mock_abspath, mock_chdir, mock_confirm):
        mock_confirm.return_value = True
        mock_abspath.return_value = '/disallowed/path/app'
        result = self.executor.execute_shell_command('cd app')
        self.assertEqual(result, "Failed to change directory to: /disallowed/path/app")
        mock_chdir.assert_not_called()

class Executor:
    def __init__(self):
        self.initial_dir = os.getcwd()
        self.current_dir = self.initial_dir
        self.allowed_directories = [self.current_dir]
        self.disallowed_commands = [
            'rmdir', 'del', 'format', 'mkfs',
            'dd', 'fsck', 'mkswap', 'mount', 'umount',
            'sudo', 'su', 'chown', 'chmod'
        ]
        self.env = os.environ.copy()

    # ... rest of the class definition ...

    # Added additional test cases for commands
    @patch('click.confirm')
    @patch('subprocess.Popen')
    def test_execute_shell_command_echo(self, mock_popen, mock_confirm):
        mock_confirm.return_value = True
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.readline.return_value = 'Hello, World!'
        mock_process.communicate.return_value = ('', '')
        mock_popen.return_value = mock_process

        result = self.executor.execute_shell_command('echo "Hello, World!"')
        self.assertEqual(result, 'Hello, World!')

    # Added test case for directory changes
    @patch('os.chdir')
    @patch('os.path.abspath')
    def test_handle_cd_command(self, mock_abspath, mock_chdir):
        mock_abspath.return_value = '/fake/path/app'
        result = self.executor._handle_cd_command('cd app')
        self.assertEqual(result, "Changed directory to: /fake/path/app")
        mock_chdir.assert_called_once_with('/fake/path/app')
        self.assertEqual(self.executor.current_dir, '/fake/path/app')

    # Mocked external dependencies in unit tests
    @patch('os.chdir')
    def test_reset_directory(self, mock_chdir):
        self.executor.current_dir = '/fake/path/app'
        self.executor.reset_directory()
        mock_chdir.assert_called_once_with(self.executor.initial_dir)
        self.assertEqual(self.executor.current_dir, self.executor.initial_dir)