import unittest\nimport sys\nfrom unittest.mock import patch, MagicMock, call\nfrom io import StringIO\nfrom drd.cli.monitor.output_monitor import OutputMonitor\n\n\nclass TestOutputMonitor(unittest.TestCase):\n\n    def setUp(self):\n        self.mock_monitor = MagicMock()\n        self.output_monitor = OutputMonitor(self.mock_monitor)\n\n    @patch('select.select')\n    @patch('time.time')\n    @patch('drd.cli.monitor.output_monitor.print_info')\n    @patch('drd.cli.monitor.output_monitor.print_prompt')\n    def test_idle_state(self, mock_print_prompt, mock_print_info, mock_time, mock_select):\n        # Setup\n        self.mock_monitor.should_stop.is_set.side_effect = [\n            False] * 10 + [True]\n        self.mock_monitor.process.poll.return_value = None\n        self.mock_monitor.processing_input.is_set.return_value = False\n        self.mock_monitor.process.stdout = MagicMock()\n        self.mock_monitor.process.stdout.readline.return_value = ""\n        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])\n\n        # Create a function to generate increasing time values\n        start_time = 1000000  # Start with a large value to avoid negative times\n\n        def time_sequence():\n            nonlocal start_time\n            start_time += 1  # Increment by 1 second each time\n            return start_time\n\n        mock_time.side_effect = time_sequence\n\n        # Capture stdout\n        captured_output = StringIO()\n        sys.stdout = captured_output\n\n        # Run\n        self.output_monitor._monitor_output()\n\n        # Restore stdout\n        sys.stdout = sys.__stdout__\n\n        # Print captured output\n        print("Captured output:")\n        print(captured_output.getvalue())\n\n        # Assert\n        expected_calls = [\n            call("\nNo more tasks to auto-process. What can I do next?\n"),\n            call("\nAvailable actions:\n"),\n            call("1. Give a coding instruction to perform\n"),\n            call("2. Process an image (type 'vision')\n"),\n            call("3. Exit monitoring mode (type 'exit')\n"),\n            call("\nType your choice or command:\n")\n        ]\n        mock_print_info.assert_has_calls(expected_calls, any_order=True)\n        mock_print_prompt.assert_called_once_with("\nNo more tasks to auto-process. What can I do next?\n")\n\nif __name__ == '__main__':\n    unittest.main()