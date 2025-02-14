import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import subprocess
from io import StringIO

# Update this import to match your actual module structure
from drd.utils.step_executor import Executor
from drd.utils.apply_file_changes import apply_changes

class TestExecutor(unittest.TestCase):

    # Existing test cases...

    def test_is_safe_path_outside_project_directory(self):
        self.executor.allowed_directories = ['/project']
        self.assertFalse(self.executor.is_safe_path('/etc/passwd'))

    def test_is_safe_rm_command_outside_project_directory(self):
        self.executor.allowed_directories = ['/project']
        self.assertFalse(self.executor.is_safe_rm_command('rm /etc/passwd'))

    def test_is_safe_command_disallowed_commands(self):
        self.assertFalse(self.executor.is_safe_command('sudo rm -rf /'))
        self.assertFalse(self.executor.is_safe_command('chmod 777 /etc/passwd'))

    def test_perform_file_operation_create_outside_project_directory(self):
        self.executor.allowed_directories = ['/project']
        with patch('click.confirm', return_value=True):
            result = self.executor.perform_file_operation('CREATE', '/etc/test.txt', 'content')
            self.assertEqual(result, "Skipping this step")

    def test_perform_file_operation_update_outside_project_directory(self):
        self.executor.allowed_directories = ['/project']
        with patch('click.confirm', return_value=True):
            result = self.executor.perform_file_operation('UPDATE', '/etc/test.txt', 'content')
            self.assertEqual(result, "Skipping this step")

    def test_perform_file_operation_delete_outside_project_directory(self):
        self.executor.allowed_directories = ['/project']
        with patch('click.confirm', return_value=True):
            result = self.executor.perform_file_operation('DELETE', '/etc/test.txt')
            self.assertEqual(result, "Skipping this step")

    def test_execute_shell_command_cd_outside_project_directory(self):
        self.executor.allowed_directories = ['/project']
        with patch('click.confirm', return_value=True):
            result = self.executor.execute_shell_command('cd /etc')
            self.assertEqual(result, "Failed to change directory to: /etc")

    def test_reset_directory(self):
        self.executor.initial_dir = '/project'
        self.executor.current_dir = '/etc'
        with patch('os.chdir') as mock_chdir:
            self.executor.reset_directory()
            mock_chdir.assert_called_once_with('/project')
            self.assertEqual(self.executor.current_dir, '/project')

# The rest of the test cases...

if __name__ == '__main__':
    unittest.main()


import subprocess
import os
import json
import click
from colorama import Fore, Style
import time
import re
from .utils import print_error, print_success, print_info, print_warning, create_confirmation_box
from .diff import preview_file_changes
from .apply_file_changes import apply_changes
from ..metadata.common_utils import get_ignore_patterns, get_folder_structure

class Executor:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.initial_dir = self.current_dir
        self.allowed_directories = [self.current_dir]
        self.disallowed_commands = [
            'rmdir', 'del', 'format', 'mkfs',
            'dd', 'fsck', 'mkswap', 'mount', 'umount',
            'sudo', 'su', 'chown', 'chmod'
        ]
        self.env = os.environ.copy()

    def is_safe_path(self, path):
        full_path = os.path.abspath(os.path.join(self.current_dir, path))
        return any(full_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories)

    def is_safe_rm_command(self, command):
        parts = command.split()
        if parts[0] != 'rm':
            return False

        # Check for dangerous flags
        dangerous_flags = ['-r', '-f', '-rf', '-fr']
        if any(flag in parts for flag in dangerous_flags):
            return False

        # Check if it's removing a specific file\n        if len(parts) != 2:\n            return False\n\n        file_to_remove = parts[1]\n        return self.is_safe_path(file_to_remove) and os.path.isfile(os.path.join(self.current_dir, file_to_remove))\n\n    def is_safe_command(self, command):\n        command_parts = command.split()\n        if command_parts[0] == 'rm':\n            return self.is_safe_rm_command(command)\n        return not any(cmd in self.disallowed_commands for cmd in command_parts)\n\n    def perform_file_operation(self, operation, filename, content=None, force=False):\n        full_path = os.path.abspath(os.path.join(self.current_dir, filename))\n\n        if not self.is_safe_path(full_path):\n            confirmation_box = create_confirmation_box(\n                filename, f"File operation is being carried out outside of the project directory. {operation.lower()} this file")\n            print(confirmation_box)\n            if not click.confirm(f"{Fore.YELLOW}Confirm {operation.lower()} [y/N]:{Style.RESET_ALL}", default=False):\n                print_info(f"File {operation.lower()} cancelled by user.")\n                return "Skipping this step"\n\n        print_info(f"File: {filename}")\n\n        # Rest of the code...\n\n    def execute_shell_command(self, command, timeout=300):  # 5 minutes timeout\n        if not self.is_safe_command(command):\n            print_warning(f"Please verify the command once: {command}")\n\n        confirmation_box = create_confirmation_box(\n            command, "execute this command")\n        print(confirmation_box)\n\n        if not click.confirm(f"{Fore.YELLOW}Confirm execution [y/N]:{Style.RESET_ALL}", default=False):\n            print_info("Command execution cancelled by user.")\n            return 'Skipping this step...'\n\n        click.echo(\n            f"{Fore.YELLOW}Executing shell command: {command}{Style.RESET_ALL}")\n\n        if command.strip().startswith(('cd', 'chdir')):\n            _, path = command.split(None, 1)\n            new_dir = os.path.abspath(os.path.join(self.current_dir, path))\n            if self.is_safe_path(new_dir):\n                os.chdir(new_dir)\n                self.current_dir = new_dir\n                print_info(f"Changed directory to: {self.current_dir}")\n                return f"Changed directory to: {self.current_dir}"\n            else:\n                print_error(f"Cannot change to directory: {new_dir}")\n                return f"Failed to change directory to: {new_dir}"\n\n        # Rest of the code...\n\n    def reset_directory(self):\n        os.chdir(self.initial_dir)\n        self.current_dir = self.initial_dir\n        print_info(f"Reset directory to: {self.current_dir}")