import unittest\nfrom unittest.mock import patch, MagicMock, call\nimport requests\nfrom drd.cli.query.main import execute_dravid_command\n\n\nclass TestExecuteDravidCommand(unittest.TestCase):\n\n    def setUp(self):\n        self.executor = MagicMock()\n        self.metadata_manager = MagicMock()\n        self.query = "Test query"\n        self.image_path = None\n        self.debug = False\n        self.instruction_prompt = None\n\n    @patch('drd.cli.query.main.Executor')\n    @patch('drd.cli.query.main.ProjectMetadataManager')\n    @patch('drd.cli.query.main.stream_dravid_api')\n    @patch('drd.cli.query.main.execute_commands')\n    @patch('drd.cli.query.main.print_debug')\n    @patch('drd.cli.query.main.print_error')\n    @patch('drd.cli.query.main.get_files_to_modify')\n    @patch('drd.cli.query.main.run_with_loader')\n    def test_execute_dravid_command_debug_mode(self, mock_run_with_loader, mock_get_files, mock_print_error,\n                                               mock_print_debug, mock_execute_commands, mock_stream_api, mock_metadata_manager, mock_executor):\n        self.debug = True\n        mock_executor.return_value = self.executor\n        mock_metadata_manager.return_value = self.metadata_manager\n        self.metadata_manager.get_project_context.return_value = "Test project context"\n        mock_get_files.return_value = ["file1.py", "file2.py"]\n\n        mock_stream_api.return_value = """\n        <response>\n            <steps>\n                <step>\n                    <type>shell</type>\n                    <command> echo \"hello\" </command>\n                </step>\n                <step>\n                    <type>file</type>\n                    <operation>CREATE</operation>\n                    <filename>text.txt</filename>\n                    <content>Test content</content>\n                </step>\n            </steps>\n        </response>\n        """\n        mock_execute_commands.return_value = (True, 2, None, "All commands executed successfully")\n        mock_run_with_loader.side_effect = lambda f, *args, **kwargs: f()\n\n        execute_dravid_command(self.query, self.image_path, self.debug, self.instruction_prompt)\n\n        mock_print_debug.assert_has_calls([call("Received 2 new command(s)")])}\n\n    @patch('drd.cli.query.main.Executor')\n    @patch('drd.cli.query.main.ProjectMetadataManager')\n    @patch('drd.cli.query.main.stream_dravid_api')\n    @patch('drd.cli.query.main.execute_commands')\n    @patch('drd.cli.query.main.handle_error_with_dravid')\n    @patch('drd.cli.query.main.print_error')\n    @patch('drd.cli.query.main.print_info')\n    @patch('drd.cli.query.main.get_files_to_modify')\n    @patch('drd.cli.query.main.run_with_loader')\n    def test_execute_dravid_command_with_error(self, mock_run_with_loader, mock_get_files, mock_print_info,\n                                               mock_print_error, mock_handle_error, mock_execute_commands, mock_stream_api, mock_metadata_manager, mock_executor):\n        mock_executor.return_value = self.executor\n        mock_metadata_manager.return_value = self.metadata_manager\n        self.metadata_manager.get_project_context.return_value = "Test project context"\n        mock_get_files.return_value = ["file1.py", "file2.py"]\n        mock_stream_api.return_value = """\n        <response>\n            <explanation>Test explanation</explanation>\n            <steps>\n                <step>\n                    <type>shell</type>\n                    <command> echo \"hello\" </command>\n                </step>\n            </steps>\n        </response>\n        """\n        mock_execute_commands.return_value = (False, 1, "Command failed", "Error output")\n        mock_handle_error.return_value = True\n        mock_run_with_loader.side_effect = lambda f, *args, **kwargs: f()\n\n        execute_dravid_command(self.query, self.image_path, self.debug, self.instruction_prompt)\n\n        mock_print_error.assert_any_call("Failed to execute command at step 1.")\n        mock_handle_error.assert_called_once()\n        mock_print_info.assert_any_call("Fix applied successfully. Continuing with the remaining commands.")}\n\n    @patch('drd.cli.query.main.Executor')\n    @patch('drd.cli.query.main.ProjectMetadataManager')\n    @patch('drd.cli.query.main.call_dravid_vision_api')\n    @patch('drd.cli.query.main.execute_commands')\n    @patch('drd.cli.query.main.print_info')\n    @patch('drd.cli.query.main.print_warning')\n    @patch('drd.cli.query.main.run_with_loader')\n    @patch('drd.cli.query.main.get_files_to_modify')  # Add this line\n    def test_execute_dravid_command_with_image(self, mock_get_files, mock_run_with_loader, mock_print_warning,\n                                               mock_print_info, mock_execute_commands, mock_call_vision_api, mock_metadata_manager, mock_executor):\n        self.image_path = "test_image.jpg"\n        mock_executor.return_value = self.executor\n        mock_metadata_manager.return_value = self.metadata_manager\n        self.metadata_manager.get_project_context.return_value = "Test project context"\n        mock_call_vision_api.return_value = [{'type': 'shell', 'command': 'echo \"Image processed\"'}]\n        mock_execute_commands.return_value = (True, 1, None, "Image command executed successfully")\n        mock_run_with_loader.side_effect = lambda f, *args, **kwargs: f()\n        mock_get_files.return_value = []  # Add this line\n\n        execute_dravid_command(self.query, self.image_path, self.debug, self.instruction_prompt)\n\n        mock_call_vision_api.assert_called_once()\n        mock_print_info.assert_any_call(f"Processing image: {self.image_path}")}\n\n    @patch('drd.cli.query.main.Executor')\n    @patch('drd.cli.query.main.ProjectMetadataManager')\n    @patch('drd.cli.query.main.get_files_to_modify')\n    @patch('drd.cli.query.main.print_error')\n    @patch('drd.cli.query.main.run_with_loader')\n    def test_execute_dravid_command_api_error(self, mock_run_with_loader, mock_print_error, mock_get_files, mock_metadata_manager, mock_executor):\n        mock_executor.return_value = self.executor\n        mock_metadata_manager.return_value = self.metadata_manager\n        self.metadata_manager.get_project_context.return_value = "Test project context"\n        mock_get_files.side_effect = requests.exceptions.ConnectionError("API connection error")\n        mock_run_with_loader.side_effect = lambda f, *args, **kwargs: f()\n\n        execute_dravid_command(self.query, self.image_path, self.debug, self.instruction_prompt)\n\n        mock_print_error.assert_called_with("An unexpected error occurred: API connection error")}\n\nif __name__ == '__main__':\n    unittest.main()