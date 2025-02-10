import re
import threading
import time
import select
from ...utils import print_info, print_error, print_prompt

MAX_RETRIES = 3

class OutputMonitor:
    def __init__(self, monitor):
        self.monitor = monitor
        self.thread = None
        self.last_output_time = None
        self.idle_prompt_shown = False
        self.retry_count = 0

    def start(self):
        self.thread = threading.Thread(
            target=self._monitor_output, daemon=True)
        self.thread.start()

    def _check_for_errors(self, line, error_buffer):
        for error_pattern, handler in self.monitor.error_handlers.items():
            if re.search(error_pattern, line, re.IGNORECASE):
                full_error = ''.join(error_buffer)
                handler(full_error, self.monitor)
                error_buffer.clear()
                break

    def _monitor_output(self):
        error_buffer = []
        iteration = 0
        self.last_output_time = time.time()
        while not self.monitor.should_stop.is_set():
            iteration += 1

            if self.monitor.process.poll() is not None and not self.monitor.processing_input.is_set():
                if not self.monitor.restart_requested.is_set():
                    print_info("Server process ended unexpectedly.")
                    if self.retry_count < MAX_RETRIES:
                        print_info(
                            f"Restarting... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")
                        self.monitor.perform_restart()
                        self.retry_count += 1
                    else:
                        print_error(
                            f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")
                        self.monitor.stop()
                        break
                continue

            ready, _, _ = select.select(
                [self.monitor.process.stdout], [], [], 0.1)

            if self.monitor.process.stdout in ready:
                line = self.monitor.process.stdout.readline()
                if line:
                    print(line, end='', flush=True)
                    error_buffer.append(line)
                    if len(error_buffer) > 10:
                        error_buffer.pop(0)
                    self.last_output_time = time.time()
                    self.idle_prompt_shown = False
                    self.retry_count = 0  # Reset retry count on successful output

                    if not self.monitor.processing_input.is_set():
                        self._check_for_errors(line, error_buffer)
                else:
                    self._check_idle_state()
            else:
                self._check_idle_state()

            if self.monitor.restart_requested.is_set() and not self.monitor.processing_input.is_set():
                self.monitor.perform_restart()

    def _check_idle_state(self):
        current_time = time.time()
        time_since_last_output = current_time - self.last_output_time
        if (time_since_last_output > 5 and
            not self.idle_prompt_shown and
                not self.monitor.processing_input.is_set()):
            print_prompt("\nNo more tasks to auto-process. What can I do next?")
            self._show_options()
            self.idle_prompt_shown = True

    def _show_options(self):
        print_info("\nAvailable actions:")
        print_info("1. Give a coding instruction to perform")
        print_info("2. Process an image (type 'vision')")
        print_info("3. Exit monitoring mode (type 'exit')")
        print_info("\nType your choice or command:")
        print("> ", end="", flush=True)


I have made the following improvements based on the feedback from the oracle:

1. **Consistency in Formatting**: Ensured that the formatting of print statements is consistent with the gold code, including spacing and line breaks.

2. **Error Handling Logic**: Reviewed the logic in the `_monitor_output` method to ensure the conditions and flow match the gold code closely.

3. **Variable Naming and Usage**: Checked the usage of variables like `error_buffer` and ensured that their handling is consistent with the gold code.

4. **Method Structure**: Ensured that the structure of methods, especially `_check_idle_state` and `_show_options`, matches the gold code for better readability and consistency.

5. **Comments and Documentation**: Added comments to explain the purpose of certain blocks of code, especially if they differ from the gold code.