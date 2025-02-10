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

    def test_is_safe_path(self):
        self.assertTrue(self.executor.is_safe_path('test.txt'))
        self.assertTrue(self.executor.is_safe_path(self.executor.current_dir))
        self.assertFalse(self.executor.is_safe_path('/etc/passwd'))

    def test_is_safe_rm_command(self):
        self.assertFalse(self.executor.is_safe_rm_command('rm test.txt'))
        with patch('os.path.isfile', return_value=True):
            self.assertTrue(self.executor.is_safe_rm_command('rm existing_file.txt'))
        self.assertFalse(self.executor.is_safe_rm_command('rm -rf /'))
        self.assertFalse(self.executor.is_safe_rm_command('rm -f test.txt'))

    def test_is_safe_command(self):
        self.assertTrue(self.executor.is_safe_command('ls'))
        self.assertFalse(self.executor.is_safe_command('sudo rm -rf /'))

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('click.confirm')
    def test_perform_file_operation_create(self, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = False
        mock_confirm.return_value = True
        result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content')
        self.assertTrue(result)
        mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')
        mock_confirm.assert_called_once()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="original content")
    @patch('click.confirm')
    @patch('drd.utils.step_executor.preview_file_changes')
    def test_perform_file_operation_update(self, mock_preview, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_confirm.return_value = True
        mock_preview.return_value = "Preview of changes"
        changes = "+ 2: This is a new line\nr 1: This is a replaced line"
        result = self.executor.perform_file_operation('UPDATE', 'test.txt', changes)
        self.assertTrue(result)
        mock_file.assert_any_call(os.path.join(self.executor.current_dir, 'test.txt'), 'r')
        mock_file.assert_any_call(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        expected_updated_content = apply_changes("original content", changes)
        mock_preview.assert_called_once_with('UPDATE', 'test.txt', new_content=expected_updated_content, original_content="original content")
        mock_file().write.assert_called_once_with(expected_updated_content)

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

    @patch('click.confirm')
    def test_perform_file_operation_user_cancel(self, mock_confirm):
        mock_confirm.return_value = False
        result = self.executor.perform_file_operation('UPDATE', 'test.txt', 'content')
        self.assertEqual(result, "Skipping this step")

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

    @patch('click.confirm')
    def test_execute_shell_command_user_cancel(self, mock_confirm):
        mock_confirm.return_value = False
        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'Skipping this step...')
        mock_confirm.assert_called_once()