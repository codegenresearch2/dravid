import unittest\"\nfrom unittest.mock import patch, mock_open, MagicMock\"\nimport os\"\nimport json\"\nimport subprocess\"\nfrom io import StringIO\"\n\"\n# Update this import to match your actual module structure\"\nfrom drd.utils.step_executor import Executor\"\nfrom drd.utils.apply_file_changes import apply_changes\"\n\"\nclass TestExecutor(unittest.TestCase):\"\n    def setUp(self):\"\n        self.executor = Executor()\"\n        self.executor.initial_dir = os.getcwd()  # Initialize with a specific directory\"\n\"\n    @patch('os.path.exists') as mock_exists,\"\n    @patch('builtins.open', new_callable=mock_open) as mock_file:\"\n        def test_perform_file_operation(self, mock_exists, mock_file):\"\n            mock_exists.return_value = False\"\n            result = self.executor.perform_file_operation('CREATE', 'test.txt', 'content')\"\n            self.assertTrue(result)\"\n            mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')\"\n            mock_file().write.assert_called_with('content')\"\n\"\n            result = self.executor.perform_file_operation('UPDATE', 'test.txt', 'updated content')\"\n            self.assertTrue(result)\"\n            mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')\"\n            mock_file().write.assert_called_with('updated content')\"\n\"\n            result = self.executor.perform_file_operation('DELETE', 'test.txt')\"\n            self.assertTrue(result)\"\n            os.path.isfile.return_value = True\"\n            os.remove.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'))\"\n\"\n    @patch('subprocess.Popen') as mock_popen:\"\n        def test_execute_shell_command(self, mock_popen):\"\n            mock_process = MagicMock()\"\n            mock_process.poll.side_effect = [None, 0]\"\n            mock_process.stdout.readline.return_value = 'output line'\"\n            mock_process.communicate.return_value = ('', '')\"\n            mock_popen.return_value = mock_process\"\n            result = self.executor.execute_shell_command('ls')\"\n            self.assertEqual(result, 'output line')\"\n\"\n    @patch('subprocess.run') as mock_run:\"\n        def test_handle_source_command(self, mock_run):\"\n            mock_run.return_value = subprocess.CompletedProcess(args=['source', 'test.sh'], returncode=0, stdout='KEY=value'\n, stderr='')\"\n            with patch('os.path.isfile', return_value=True):\"\n                result = self.executor._handle_source_command('source test.sh')\"\n            self.assertEqual(result, "Source command executed successfully")\"\n            self.assertEqual(self.executor.env['KEY'], 'value')\"\n\"\n    def test_update_env_from_command(self):\"\n        # Test simple assignment\"\n        self.executor._update_env_from_command('TEST_VAR=test_value')\"\n        self.assertEqual(self.executor.env['TEST_VAR'], 'test_value')\"\n        \"\n        # Test export command\"\n        self.executor._update_env_from_command('export EXPORT_VAR=export_value')\"\n        self.assertEqual(self.executor.env['EXPORT_VAR'], 'export_value')\"\n        \"\n        # Test set command\"\n        self.executor._update_env_from_command('set SET_VAR=set_value')\"\n        self.assertEqual(self.executor.env['SET_VAR'], 'set_value')\"\n        \"\n        # Test with quotes\"\n        self.executor._update_env_from_command('QUOTE_VAR=