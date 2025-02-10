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
        self.allowed_directories = [self.current_dir, '/example/path']  # Add example path
        self.disallowed_commands = ['rmdir', 'del', 'format', 'mkfs', 'dd', 'fsck', 'mkswap', 'mount', 'umount', 'sudo', 'su', 'chown', 'chmod']
        self.env = os.environ.copy()

    def is_safe_path(self, path):
        full_path = os.path.abspath(os.path.join(self.current_dir, path))
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
        return self.is_safe_path(file_to_remove) and os.path.isfile(os.path.join(self.current_dir, file_to_remove))

    # Rest of the code remains the same