import unittest
import sys
import logging
from unittest.mock import patch, MagicMock, call
from io import StringIO
from drd.cli.monitor.output_monitor import OutputMonitor
from drd.utils import print_info, print_prompt

def setup_logger():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def print_command_details():
    print_info("\nAvailable actions:")
    print_info("1. Give a coding instruction to perform")
    print_info("2. Process an image (type 'vision')")
    print_info("3. Exit monitoring mode (type 'exit')")
    print_prompt("\nType your choice or command:")

class TestOutputMonitor(unittest.TestCase):

    def setUp(self):
        self.mock_monitor = MagicMock()
        self.output_monitor = OutputMonitor(self.mock_monitor)
        setup_logger()

    @patch('select.select')
    @patch('time.time')
    @patch('drd.utils.print_info')
    @patch('drd.utils.print_prompt')
    def test_idle_state(self, mock_print_prompt, mock_print_info, mock_time, mock_select):
        # Setup
        self.mock_monitor.should_stop.is_set.side_effect = [False] * 10 + [True]
        self.mock_monitor.process.poll.return_value = None
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock()
        self.mock_monitor.process.stdout.readline.return_value = ""
        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])
        mock_time.side_effect = [0] + [6] * 10  # Simulate time passing

        # Run
        self.output_monitor._monitor_output()

        # Assert
        expected_calls = [
            call("\nNo more tasks to auto-process. What can I do next?"),
            call("\nAvailable actions:"),
            call("1. Give a coding instruction to perform"),
            call("2. Process an image (type 'vision')"),
            call("3. Exit monitoring mode (type 'exit')"),
        ]
        mock_print_info.assert_has_calls(expected_calls, any_order=True)
        mock_print_prompt.assert_called_once_with("\nType your choice or command:")

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

if __name__ == '__main__':
    unittest.main()