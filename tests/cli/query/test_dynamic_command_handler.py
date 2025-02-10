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
        self.executor.initial_dir = '/initial/dir'
        self.executor.current_dir = '/initial/dir'

    # ... rest of the code ...

    @patch('os.chdir')
    def test_reset_directory(self, mock_chdir):
        self.executor.current_dir = '/fake/path/app'
        self.executor.reset_directory()
        mock_chdir.assert_called_once_with(self.executor.initial_dir)
        self.assertEqual(self.executor.current_dir, self.executor.initial_dir)

# Added a call to os.chdir(self.initial_dir) to fix the test failure
def reset_directory(self):
    os.chdir(self.initial_dir)
    self.current_dir = self.initial_dir

if __name__ == '__main__':
    unittest.main()