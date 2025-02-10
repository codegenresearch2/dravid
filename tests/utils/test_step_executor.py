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
    def test_perform_file_operation(self, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = False
        mock_confirm.return_value = True
        result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content')
        self.assertTrue(result)
        mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')
        mock_confirm.assert_called_once()

        mock_exists.return_value = True
        mock_confirm.return_value = True
        changes = "+ 2: This is a new line\nr 1: This is a replaced line"
        result = self.executor.perform_file_operation('UPDATE', 'test.txt', changes)
        self.assertTrue(result)
        mock_file.assert_any_call(os.path.join(self.executor.current_dir, 'test.txt'), 'r')
        mock_file.assert_any_call(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        expected_updated_content = apply_changes("original content", changes)
        mock_file().write.assert_called_with(expected_updated_content)

        mock_confirm.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result)

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

        mock_confirm.return_value = False
        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'Skipping this step...')
        mock_confirm.assert_called()

    def test_parse_json(self):
        valid_json = '{"key": "value"}'
        invalid_json = '{key: value}'
        self.assertEqual(self.executor.parse_json(valid_json), {"key": "value"})
        self.assertIsNone(self.executor.parse_json(invalid_json))

    def test_merge_json(self):
        existing_content = '{"key1": "value1"}'
        new_content = '{"key2": "value2"}'
        expected_result = json.dumps({"key1": "value1", "key2": "value2"}, indent=2)
        self.assertEqual(self.executor.merge_json(existing_content, new_content), expected_result)

    @patch('drd.utils.step_executor.get_ignore_patterns')
    @patch('drd.utils.step_executor.get_folder_structure')
    def test_get_folder_structure(self, mock_get_folder_structure, mock_get_ignore_patterns):
        mock_get_ignore_patterns.return_value = ([], None)
        mock_get_folder_structure.return_value = {'folder': {'file.txt': 'file'}}
        result = self.executor.get_folder_structure()
        self.assertEqual(result, {'folder': {'file.txt': 'file'}})