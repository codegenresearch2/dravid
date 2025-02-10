import subprocess
import os
import json
import click
from colorama import Fore, Style
import time
from .utils import print_error, print_success, print_info, print_warning, create_confirmation_box
from .diff import preview_file_changes
from .apply_file_changes import apply_changes
from ..metadata.common_utils import get_ignore_patterns, get_folder_structure

class Executor:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.initial_dir = self.current_dir
        self.allowed_directories = [self.current_dir, '/fake/path']  # Update example path
        self.disallowed_commands = ['rmdir', 'del', 'format', 'mkfs', 'dd', 'fsck', 'mkswap', 'mount', 'umount', 'sudo', 'su', 'chown', 'chmod']
        self.env = os.environ.copy()

    def is_safe_path(self, path):
        full_path = os.path.abspath(path)
        return full_path == self.current_dir or any(full_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories)

    def is_safe_rm_command(self, command):
        parts = command.split()
        if parts[0] != 'rm':
            return False
        dangerous_flags = ['-r', '-f', '-rf', '-fr']
        if any(flag in parts for flag in dangerous_flags):
            return False
        if len(parts) != 2:
            return False
        file_to_remove = parts[1]
        return self.is_safe_path(file_to_remove) and os.path.isfile(file_to_remove)

    def is_safe_command(self, command):
        command_parts = command.split()
        if command_parts[0] == 'rm':
            return self.is_safe_rm_command(command)
        return not any(cmd in self.disallowed_commands for cmd in command_parts)

    def perform_file_operation(self, operation, filename, content=None, force=False):
        full_path = os.path.abspath(os.path.join(self.current_dir, filename))

        if not self.is_safe_path(full_path):
            confirmation_box = create_confirmation_box(filename, f"File operation is being carried out outside of the project directory. {operation.lower()} this file")
            print(confirmation_box)
            if not click.confirm(f"{Fore.YELLOW}Confirm {operation.lower()} [y/N]:{Style.RESET_ALL}", default=False):
                print_info(f"File {operation.lower()} cancelled by user.")
                return False

        print_info(f"File: {filename}")

        if operation == 'CREATE':
            # Implement file creation logic here
            # Return True if successful, False otherwise
            pass
        elif operation == 'UPDATE':
            # Implement file update logic here
            # Return True if successful, False otherwise
            pass
        elif operation == 'DELETE':
            # Implement file deletion logic here
            # Return True if successful, False otherwise
            pass
        else:
            print_error(f"Unknown file operation: {operation}")
            return False

    def parse_json(self, json_string):
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print_error(f"JSON parsing error: {str(e)}")
            return None

    def merge_json(self, existing_content, new_content):
        try:
            existing_json = json.loads(existing_content)
            new_json = json.loads(new_content)
            merged_json = {**existing_json, **new_json}
            return json.dumps(merged_json, indent=2)
        except json.JSONDecodeError as e:
            print_error(f"Error merging JSON content: {str(e)}")
            return None

    def get_folder_structure(self):
        ignore_patterns, _ = get_ignore_patterns(self.current_dir)
        return get_folder_structure(self.current_dir, ignore_patterns)

    def execute_shell_command(self, command, timeout=300):
        if not self.is_safe_command(command):
            print_warning(f"Please verify the command once: {command}")

        confirmation_box = create_confirmation_box(command, "execute this command")
        print(confirmation_box)

        if not click.confirm(f"{Fore.YELLOW}Confirm execution [y/N]:{Style.RESET_ALL}", default=False):
            print_info("Command execution cancelled by user.")
            return 'Skipping this step...'

        if command.strip().startswith(('cd', 'chdir')):
            return self._handle_cd_command(command)
        elif command.strip().startswith(('source', '.')):
            return self._handle_source_command(command)
        else:
            return self._execute_single_command(command, timeout)

    def _execute_single_command(self, command, timeout):
        # Implement single command execution logic here
        # Return the output of the command if successful, raise an exception otherwise
        pass

    def _handle_source_command(self, command):
        # Implement source command handling logic here
        # Return a success message if successful, raise an exception otherwise
        pass

    def _update_env_from_command(self, command):
        if '=' in command:
            if command.startswith('export '):
                _, var_assignment = command.split(None, 1)
                key, value = var_assignment.split('=', 1)
                self.env[key.strip()] = value.strip().strip('"\'')
            elif command.startswith('set '):
                _, var_assignment = command.split(None, 1)
                key, value = var_assignment.split('=', 1)
                self.env[key.strip()] = value.strip().strip('"\'')
            else:
                key, value = command.split('=', 1)
                self.env[key.strip()] = value.strip().strip('"\'')

    def _handle_cd_command(self, command):
        _, path = command.split(None, 1)
        new_dir = os.path.abspath(os.path.join(self.current_dir, path))
        if self.is_safe_path(new_dir):
            os.chdir(new_dir)
            self.current_dir = new_dir
            print_info(f"Changed directory to: {self.current_dir}")
            return f"Changed directory to: {self.current_dir}"
        else:
            print_error(f"Cannot change to directory: {new_dir}")
            return f"Failed to change directory to: {new_dir}"

    def reset_directory(self):
        os.chdir(self.initial_dir)
        self.current_dir = self.initial_dir
        print_info(f"Reset directory to: {self.current_dir}")