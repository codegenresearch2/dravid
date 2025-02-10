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
    def test_is_safe_rm_command(self):
        # Test with a file that exists in the current directory
        with patch('os.path.isfile', return_value=True):
            self.assertTrue(self.executor.is_safe_rm_command('rm existing_file.txt'))
        self.assertFalse(self.executor.is_safe_rm_command('rm -rf /'))
        self.assertFalse(self.executor.is_safe_rm_command('rm -f test.txt'))

    # Consolidated tests and improved assertions
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_perform_file_operation_create(self, mock_file, mock_exists):
        mock_exists.return_value = False
        result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content')
        self.assertTrue(result)
        mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')

        mock_exists.return_value = True
        result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content')
        self.assertEqual(result, 'Skipping this step')

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.remove')
    def test_perform_file_operation_delete(self, mock_remove, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result)
        mock_remove.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'))

        mock_exists.return_value = False
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertEqual(result, 'Skipping this step')

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