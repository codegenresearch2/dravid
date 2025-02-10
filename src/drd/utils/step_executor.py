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

# Define constants for consistency
CONFIRMATION_PROMPT = f"{Fore.YELLOW}Confirm [y/N]:{Style.RESET_ALL}"
ERROR_PREFIX = "Error"
SUCCESS_PREFIX = "Success"
WARNING_PREFIX = "Warning"

class Executor:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.allowed_directories = [self.current_dir, '/fake/path']
        self.initial_dir = self.current_dir
        self.disallowed_commands = [
            'rmdir', 'del', 'format', 'mkfs',
            'dd', 'fsck', 'mkswap', 'mount', 'umount',
            'sudo', 'su', 'chown', 'chmod'
        ]
        self.env = os.environ.copy()

    def is_safe_path(self, path):
        full_path = os.path.abspath(path)
        return any(full_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories) or full_path == self.current_dir

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
        return self.is_safe_path(file_to_remove) and os.path.isfile(os.path.join(self.current_dir, file_to_remove))

    def is_safe_command(self, command):
        command_parts = command.split()
        if command_parts[0] == 'rm':
            return self.is_safe_rm_command(command)
        return not any(cmd in self.disallowed_commands for cmd in command_parts)

    def perform_file_operation(self, operation, filename, content=None, force=False):
        full_path = os.path.abspath(os.path.join(self.current_dir, filename))

        if not self.is_safe_path(full_path):
            confirmation_box = create_confirmation_box(
                filename, f"File operation outside project directory. {operation.lower()} this file?")
            print(confirmation_box)
            if not click.confirm(CONFIRMATION_PROMPT, default=False):
                print_info(f"File {operation.lower()} cancelled by user.")
                return "Skipping this step"

        print_info(f"File: {filename}")

        if operation == 'CREATE':
            return self._perform_create_operation(filename, content, force)
        elif operation == 'UPDATE':
            return self._perform_update_operation(filename, content)
        elif operation == 'DELETE':
            return self._perform_delete_operation(filename)
        else:
            print_error(f"{ERROR_PREFIX}: Unknown file operation: {operation}")
            return False

    def _perform_create_operation(self, filename, content, force):
        if os.path.exists(filename) and not force:
            print_info(f"File already exists: {filename}")
            return False
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            preview = preview_file_changes('CREATE', filename, new_content=content)
            print(preview)
            if click.confirm(CONFIRMATION_PROMPT, default=False):
                with open(filename, 'w') as f:
                    f.write(content)
                print_success(f"{SUCCESS_PREFIX}: File created successfully: {filename}")
                return True
            else:
                print_info("File creation cancelled by user.")
                return "Skipping this step"
        except Exception as e:
            print_error(f"{ERROR_PREFIX} creating file: {str(e)}")
            return False

    def _perform_update_operation(self, filename, content):
        if not os.path.exists(filename):
            print_info(f"File does not exist: {filename}")
            return False
        try:
            with open(filename, 'r') as f:
                original_content = f.read()

            if content:
                updated_content = apply_changes(original_content, content)
                preview = preview_file_changes('UPDATE', filename, new_content=updated_content, original_content=original_content)
                print(preview)
                confirmation_box = create_confirmation_box(filename, "update this file?")
                print(confirmation_box)

                if click.confirm(CONFIRMATION_PROMPT, default=False):
                    with open(filename, 'w') as f:
                        f.write(updated_content)
                    print_success(f"{SUCCESS_PREFIX}: File updated successfully: {filename}")
                    return True
                else:
                    print_info("File update cancelled by user.")
                    return "Skipping this step"
            else:
                print_error(f"{ERROR_PREFIX}: No content or changes provided for update operation")
                return False
        except Exception as e:
            print_error(f"{ERROR_PREFIX} updating file: {str(e)}")
            return False

    def _perform_delete_operation(self, filename):
        if not os.path.isfile(filename):
            print_info(f"Delete operation is only allowed for files: {filename}")
            return False
        confirmation_box = create_confirmation_box(filename, "delete this file?")
        print(confirmation_box)
        if click.confirm(CONFIRMATION_PROMPT, default=False):
            try:
                os.remove(filename)
                print_success(f"{SUCCESS_PREFIX}: File deleted successfully: {filename}")
                return True
            except Exception as e:
                print_error(f"{ERROR_PREFIX} deleting file: {str(e)}")
                return False
        else:
            print_info("File deletion cancelled by user.")
            return "Skipping this step"

    # Rest of the code remains the same