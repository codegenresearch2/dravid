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
        self.allowed_directories = [self.current_dir, '/fake/path']
        self.disallowed_commands = [
            'rmdir', 'del', 'format', 'mkfs',
            'dd', 'fsck', 'mkswap', 'mount', 'umount',
            'sudo', 'su', 'chown', 'chmod'
        ]
        self.env = os.environ.copy()

    def is_safe_path(self, path):
        full_path = os.path.abspath(os.path.join(self.current_dir, path))
        return any(full_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories) or full_path == self.current_dir

    # Rest of the code remains the same