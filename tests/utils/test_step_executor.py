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

    def setUp(self):
        self.executor = Executor()
        self.executor.initial_dir = self.executor.current_dir

    # ... other tests ...

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.remove')
    @patch('click.confirm')
    def test_perform_file_operation_delete(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_confirm.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result)
        mock_remove.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'))
        mock_confirm.assert_called_once()

    # ... other tests ...

    @patch('subprocess.Popen')
    @patch('click.confirm')
    def test_execute_shell_command(self, mock_confirm, mock_popen):
        mock_confirm.return_value = True
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.readline.return_value = 'output line'
        mock_process.communicate.return_value = ('', '')
        mock_popen.return_value = mock_process
        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'output line')
        mock_confirm.assert_called_once()

        mock_confirm.return_value = False
        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'Skipping this step...')
        mock_confirm.assert_called()

    # ... other tests ...