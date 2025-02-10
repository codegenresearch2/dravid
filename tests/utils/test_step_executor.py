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

    # Improved test method naming
    def test_is_safe_path(self):
        self.assertTrue(self.executor.is_safe_path('test.txt'))
        self.assertTrue(self.executor.is_safe_path(self.executor.current_dir))
        self.assertFalse(self.executor.is_safe_path('/etc/passwd'))

    def test_is_safe_command(self):
        self.assertTrue(self.executor.is_safe_command('ls'))
        self.assertFalse(self.executor.is_safe_command('sudo rm -rf /'))

    # Consolidated tests and improved assertions
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_create(self, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = False
        result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content')
        self.assertTrue(result)
        mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')

        mock_exists.return_value = True
        result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content', force=True)
        self.assertTrue(result)

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.remove')
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result)
        mock_remove.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'))

        mock_exists.return_value = False
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertEqual(result, False)

    # Additional test cases for edge cases or additional functionality
    def test_perform_file_operation_update_file_not_exists(self):
        with patch('os.path.exists', return_value=False):
            result = self.executor.perform_file_operation('UPDATE', 'test.txt', 'content')
            self.assertEqual(result, False)

    def test_perform_file_operation_update_no_changes(self):
        with patch('os.path.exists', return_value=True):
            result = self.executor.perform_file_operation('UPDATE', 'test.txt', None)
            self.assertEqual(result, False)

    # ... other tests ...