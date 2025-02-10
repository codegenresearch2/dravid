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
        self.disallowed_commands = [
            'rmdir', 'del', 'format', 'mkfs',
            'dd', 'fsck', 'mkswap', 'mount', 'umount',
            'sudo', 'su', 'chown', 'chmod'
        ]
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
            if os.path.exists(full_path) and not force:
                print_info(f"File already exists: {filename}")
                return False
            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
                print_success(f"File created successfully: {filename}")
                return True
            except Exception as e:
                print_error(f"Error creating file: {str(e)}")
                return False

        elif operation == 'UPDATE':
            # Implement file update logic here
            # Return True if successful, False otherwise
            if not os.path.exists(full_path):
                print_info(f"File does not exist: {filename}")
                return False
            try:
                with open(full_path, 'w') as f:
                    f.write(content)
                print_success(f"File updated successfully: {filename}")
                return True
            except Exception as e:
                print_error(f"Error updating file: {str(e)}")
                return False

        elif operation == 'DELETE':
            # Implement file deletion logic here
            # Return True if successful, False otherwise
            if not os.path.isfile(full_path):
                print_info(f"Delete operation is only allowed for files: {filename}")
                return False
            try:
                os.remove(full_path)
                print_success(f"File deleted successfully: {filename}")
                return True
            except Exception as e:
                print_error(f"Error deleting file: {str(e)}")
                return False

        else:
            print_error(f"Unknown file operation: {operation}")
            return False

    # Rest of the code remains the same