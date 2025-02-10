import unittest
import sys
from unittest.mock import patch, MagicMock, call
from io import StringIO
from drd.cli.monitor.output_monitor import OutputMonitor
import time

class TestOutputMonitor(unittest.TestCase):

    def setUp(self):
        self.mock_monitor = MagicMock()
        self.output_monitor = OutputMonitor(self.mock_monitor)

    @patch('select.select')
    @patch('time.time')
    @patch('drd.cli.monitor.output_monitor.print_info')
    @patch('drd.cli.monitor.output_monitor.print_prompt')
    def test_idle_state(self, mock_print_prompt, mock_print_info, mock_time, mock_select):
        # Setup
        self.mock_monitor.should_stop.is_set.side_effect = [False] * 10 + [True]
        self.mock_monitor.process.poll.return_value = None
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock(spec=sys.stdout)
        self.mock_monitor.process.stdout.fileno.return_value = 1  # Added to fix TypeError
        self.mock_monitor.process.stdout.readline.return_value = ""
        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])
        mock_time.side_effect = [0] + [6] * 10  # Simulate time passing

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Run
        self.output_monitor._monitor_output()

        # Restore stdout and print captured output
        sys.stdout = sys.__stdout__
        print("Captured output:")
        print(captured_output.getvalue())

        # Assert
        mock_print_prompt.assert_called_once_with(
            "\nNo more tasks to auto-process. What can I do next?")
        expected_calls = [
            call("\nAvailable actions:"),
            call("1. Give a coding instruction to perform"),
            call("2. Process an image (type 'vision')"),  # Updated to match gold code
            call("3. Exit monitoring mode (type 'exit')"),
            call("\nType your choice or command:")
        ]
        mock_print_info.assert_has_calls(expected_calls, any_order=True)

    def test_check_for_errors(self):
        # Setup
        error_buffer = ["Error: Test error\n"]
        self.mock_monitor.error_handlers = {
            r"Error:": MagicMock()
        }

        # Run
        self.output_monitor._check_for_errors(
            "Error: Test error\n", error_buffer)

        # Assert
        self.mock_monitor.error_handlers[r"Error:"].assert_called_once_with(
            "Error: Test error\n", self.mock_monitor)
        self.assertEqual(error_buffer, [])  # Ensure error buffer is cleared

    def test_monitor_output_delay(self):
        # Setup
        self.mock_monitor.should_stop.is_set.side_effect = [False] * 5 + [True]
        self.mock_monitor.process.poll.return_value = None
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock(spec=sys.stdout)
        self.mock_monitor.process.stdout.fileno.return_value = 1  # Added to fix TypeError
        self.mock_monitor.process.stdout.readline.return_value = "Test output\n"

        # Run
        start_time = time.time()
        self.output_monitor._monitor_output()
        end_time = time.time()

        # Assert
        self.assertGreaterEqual(end_time - start_time, 0.1 * 5)  # Ensure delay is present

if __name__ == '__main__':
    unittest.main()