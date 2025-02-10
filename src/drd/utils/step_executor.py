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

# Define constants for messages and operations
OPERATION_MESSAGES = {
    'CREATE': 'File created successfully',
    'UPDATE': 'File updated successfully',
    'DELETE': 'File deleted successfully'
}

ERROR_MESSAGES = {
    'CREATE': 'Error creating file',
    'UPDATE': 'Error updating file',
    'DELETE': 'Error deleting file'
}

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
            confirmation_box = create_confirmation_box(filename, f"⚠️ File operation is being carried out outside of the project directory. {operation.lower()} this file")
            print(confirmation_box)
            if not click.confirm(f"{Fore.YELLOW}Confirm {operation.lower()} [y/N]:{Style.RESET_ALL}", default=False):
                print_info(f"🚫 File {operation.lower()} cancelled by user.")
                return "Skipping this step"
        print_info(f"📁 File: {filename}")
        if operation not in ['CREATE', 'UPDATE', 'DELETE']:
            print_error(f"🚨 Unknown file operation: {operation}")
            return False
        try:
            updated_content = None  # Initialize updated_content
            if operation == 'CREATE':
                if os.path.exists(full_path) and not force:
                    print_info(f"📝 File already exists: {filename}")
                    return False
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
            elif operation == 'UPDATE':
                if not os.path.exists(full_path):
                    print_info(f"📝 File does not exist: {filename}")
                    return False
                with open(full_path, 'r') as f:
                    original_content = f.read()
                if content:
                    updated_content = apply_changes(original_content, content)
                else:
                    print_error("🚨 No content or changes provided for update operation")
                    return False
            elif operation == 'DELETE':
                if not os.path.isfile(full_path):
                    print_info(f"🚫 Delete operation is only allowed for files: {filename}")
                    return False
            preview = preview_file_changes(operation, filename, new_content=updated_content if operation != 'DELETE' else None, original_content=original_content if operation == 'UPDATE' else None)
            print(preview)
            if operation == 'DELETE':
                confirmation_box = create_confirmation_box(filename, f"{operation.lower()} this file")
                print(confirmation_box)
                if not click.confirm(f"{Fore.YELLOW}Confirm deletion [y/N]:{Style.RESET_ALL}", default=False):
                    print_info("🚫 File deletion cancelled by user.")
                    return "Skipping this step"
            if click.confirm(f"{Fore.YELLOW}Confirm {operation.lower()} [y/N]:{Style.RESET_ALL}", default=False):
                if operation == 'CREATE' or operation == 'UPDATE':
                    with open(full_path, 'w') as f:
                        f.write(content if operation == 'CREATE' else updated_content)
                elif operation == 'DELETE':
                    os.remove(full_path)
                print_success(f"🎉 {OPERATION_MESSAGES[operation]}: {filename}")
                return True
            else:
                print_info(f"🚫 File {operation.lower()} cancelled by user.")
                return "Skipping this step"
        except Exception as e:
            print_error(f"🚨 {ERROR_MESSAGES[operation]}: {str(e)}")
            return False

    # Rest of the code remains the same