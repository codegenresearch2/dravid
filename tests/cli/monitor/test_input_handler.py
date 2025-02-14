import unittest
import threading
from unittest.mock import patch, MagicMock
from drd.cli.monitor.input_handler import InputHandler
from drd.utils import print_info

class TestInputHandler(unittest.TestCase):

    def setUp(self):
        self.mock_monitor = MagicMock()
        self.input_handler = InputHandler(self.mock_monitor)

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    @patch('drd.cli.monitor.input_handler.input', side_effect=['test input', 'exit'])
    def test_handle_input(self, mock_input, mock_execute_command):
        self.mock_monitor.should_stop.is_set.side_effect = [False, False, True]

        def run_input_handler():
            self.input_handler._handle_input()

        thread = threading.Thread(target=run_input_handler)
        thread.start()

        thread.join(timeout=10)

        if thread.is_alive():
            self.fail("_handle_input did not complete within the timeout period")

        self.mock_monitor.stop.assert_called_once()
        self.assertEqual(mock_input.call_count, 2)
        mock_execute_command.assert_called_once()

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    def test_process_input(self, mock_execute_command):
        self.mock_monitor.processing_input = MagicMock()
        self.input_handler._process_input('test command')
        mock_execute_command.assert_called_once()
        self.mock_monitor.processing_input.set.assert_called_once()
        self.mock_monitor.processing_input.clear.assert_called_once()

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    @patch('drd.cli.monitor.input_handler.InputHandler._get_input_with_autocomplete', return_value='/path/to/image.jpg')
    @patch('drd.cli.monitor.input_handler.input', return_value='process this image')
    @patch('os.path.exists', return_value=True)
    def test_handle_vision_input(self, mock_exists, mock_input, mock_autocomplete, mock_execute_command):
        self.mock_monitor.processing_input = MagicMock()
        self.input_handler._handle_vision_input()
        mock_execute_command.assert_called_once()
        self.mock_monitor.processing_input.set.assert_called_once()
        self.mock_monitor.processing_input.clear.assert_called_once()

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    @patch('drd.cli.monitor.input_handler.InputHandler._get_input_with_autocomplete', return_value='/path/to/image.jpg')
    @patch('drd.cli.monitor.input_handler.input', return_value='process this image')
    @patch('os.path.exists', return_value=False)
    def test_handle_vision_input_file_not_found(self, mock_exists, mock_input, mock_autocomplete, mock_execute_command):
        self.mock_monitor.processing_input = MagicMock()
        self.input_handler._handle_vision_input()
        mock_execute_command.assert_not_called()
        self.mock_monitor.processing_input.set.assert_not_called()
        self.mock_monitor.processing_input.clear.assert_not_called()

    @patch('drd.cli.monitor.input_handler.click.getchar', side_effect=['\t', '\r'])
    @patch('drd.cli.monitor.input_handler.InputHandler._autocomplete', return_value=['/path/to/file.txt'])
    @patch('drd.cli.monitor.input_handler.click.echo')
    def test_get_input_with_autocomplete(self, mock_echo, mock_autocomplete, mock_getchar):
        result = self.input_handler._get_input_with_autocomplete()
        self.assertEqual(result, '/path/to/file.txt')
        mock_autocomplete.assert_called_once()

    @patch('glob.glob', return_value=['/path/to/file.txt'])
    def test_autocomplete(self, mock_glob):
        result = self.input_handler._autocomplete('/path/to/f')
        self.assertEqual(result, ['/path/to/file.txt'])
        mock_glob.assert_called_once_with('/path/to/f*')

    def test_handle_general_input(self):
        with patch('drd.cli.monitor.input_handler.execute_dravid_command') as mock_execute_command:
            self.input_handler._handle_general_input('process this image /path/to/image.jpg')
            mock_execute_command.assert_called_once()

        with patch('drd.cli.monitor.input_handler.execute_dravid_command') as mock_execute_command:
            self.input_handler._handle_general_input('do something else')
            mock_execute_command.assert_called_once()

    def test_handle_general_input_file_not_found(self):
        with patch('drd.cli.monitor.input_handler.execute_dravid_command') as mock_execute_command, \
             patch('drd.cli.monitor.input_handler.print_error') as mock_print_error, \
             patch('os.path.exists', return_value=False):
            self.input_handler._handle_general_input('process this image /path/to/nonexistent.jpg')
            mock_execute_command.assert_not_called()
            mock_print_error.assert_called_once()

    def test_check_for_errors(self):
        error_buffer = ["Error: Test error\n"]
        self.mock_monitor.error_handlers = {
            r"Error:": MagicMock()
        }

        self.input_handler._check_for_errors(
            "Error: Test error\n", error_buffer)

        self.mock_monitor.error_handlers[r"Error:"].assert_called_once_with(
            "Error: Test error\n", self.mock_monitor)

    def test_idle_state(self):
        self.mock_monitor.should_stop.is_set.side_effect = [
            False] * 10 + [True]
        self.mock_monitor.process.poll.return_value = None
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock()
        self.mock_monitor.process.stdout.readline.return_value = ""

        with patch('select.select') as mock_select, \
             patch('time.time') as mock_time, \
             patch('drd.cli.monitor.input_handler.print_info') as mock_print_info, \
             patch('drd.cli.monitor.input_handler.print_prompt') as mock_print_prompt:

            mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])
            mock_time.side_effect = [0] + [6] * 10

            self.input_handler._monitor_output()

            mock_print_prompt.assert_called_once_with(
                "\nNo more tasks to auto-process. Please provide instructions or specify an action:")
            expected_calls = [
                call("\nAvailable actions:"),
                call("1. Provide a coding instruction"),
                call("2. Provide a coding instruction with file autocomplete (type 'p')"),
                call("3. Exit monitoring mode (type 'exit')"),
                call("\nType your choice or command:")
            ]
            mock_print_info.assert_has_calls(expected_calls, any_order=True)


In the rewritten code, I have added processing flags to the `InputHandler` class to indicate when input is being processed. I have also simplified error handling in the `_check_for_errors` method and enhanced user instructions for better clarity in the `_monitor_output` method.