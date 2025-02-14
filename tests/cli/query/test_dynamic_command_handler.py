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
        self.executor.initial_dir = self.initial_dir
        self.executor.current_dir = self.initial_dir

    # Test methods remain the same, but references to self.executor.current_dir are updated

    @patch('os.chdir')
    def test_handle_cd_command(self, mock_chdir):
        target_dir = 'app'
        abs_target_dir = os.path.join(self.initial_dir, target_dir)
        mock_chdir.return_value = None
        result = self.executor._handle_cd_command(f'cd {target_dir}')
        self.assertEqual(result, f"Changed directory to: {abs_target_dir}")
        mock_chdir.assert_called_once_with(abs_target_dir)
        self.assertEqual(self.executor.current_dir, abs_target_dir)

    # Other test methods remain the same

    @patch('os.chdir')
    def test_reset_directory(self, mock_chdir):
        self.executor.current_dir = '/fake/path/app'
        self.executor.reset_directory()
        mock_chdir.assert_called_once_with(self.initial_dir)
        self.assertEqual(self.executor.current_dir, self.initial_dir)