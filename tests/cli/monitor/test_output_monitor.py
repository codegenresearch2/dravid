import unittest
import sys
import logging
from unittest.mock import patch, MagicMock, call
from io import StringIO
from drd.cli.monitor.output_monitor import OutputMonitor

def setup_logger():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

def print_command_details():
    logging.info("\nAvailable actions:")
    logging.info("1. Give a coding instruction to perform")
    logging.info("2. Process an image (type 'vision')")
    logging.info("3. Exit monitoring mode (type 'exit')")
    logging.info("\nType your choice or command:")

class TestOutputMonitor(unittest.TestCase):

    def setUp(self):
        setup_logger()
        self.mock_monitor = MagicMock()
        self.output_monitor = OutputMonitor(self.mock_monitor)

    @patch('select.select')
    @patch('time.time')
    def test_idle_state(self, mock_time, mock_select):
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
        self.assertEqual(self.output_monitor.idle_prompt_shown, True)

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