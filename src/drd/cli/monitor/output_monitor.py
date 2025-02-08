import re\\\\nimport threading\\\nimport time\\\nimport select\\\nfrom ...utils import print_info, print_error, print_prompt\\\\n\\\\nMAX_RETRIES = 3\\\\n\\\\nclass OutputMonitor:\\\\n    def __init__(self, monitor):\\\\n        self.monitor = monitor\\\\n        self.thread = None\\\\n        self.last_output_time = None\\\\n        self.idle_prompt_shown = False\\\\n        self.retry_count = 0\\\\n\\\\n    def start(self):\\\\n        self.thread = threading.Thread(target=self._monitor_output, daemon=True)\\\\n        self.thread.start()\\\\n\\\\n    def _check_for_errors(self, line, error_buffer):\\\\n        for error_pattern, handler in self.monitor.error_handlers.items():\\\\n            if re.search(error_pattern, line, re.IGNORECASE):\\\\n                full_error = ''.join(error_buffer)\\\\n                handler(full_error, self.monitor)\\\\n                error_buffer.clear()\\\\n                break\\\\n\\\\n    def _monitor_output(self):\\\\n        error_buffer = []\\\\n        iteration = 0\\\\n        self.last_output_time = time.time()\\\\n        while not self.monitor.should_stop.is_set():\\\\n            iteration += 1\\\\n\\\\n            if self.monitor.process.poll() is not None and not self.monitor.processing_input.is_set():\\\\n                if not self.monitor.restart_requested.is_set():\\\\n                    print_info("Server process ended unexpectedly.")\\\\n                    if self.retry_count < MAX_RETRIES:\\\\n                        print_info(\\\\n                            f"Restarting... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")\\\\n                        self.monitor.perform_restart()\\\\n                        self.retry_count += 1\\\\n                    else:\\\\n                        print_error(\\\\n                            f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")\\\\n                        self.monitor.stop()\\\\n                        break\\\\n                continue\\\\n\\\\n            ready, _, _ = select.select([self.monitor.process.stdout], [], [], 0.1)\\\\n\\\\n            if self.monitor.process.stdout in ready:\\\\n                line = self.monitor.process.stdout.readline()\\\\n                if line:\\\\n                    print(line, end='', flush=True)\\\\n                    error_buffer.append(line)\\\\n                    if len(error_buffer) > 10:\\\\n                        error_buffer.pop(0)\\\\n                    self.last_output_time = time.time()\\\\n                    self.idle_prompt_shown = False\\\\n                    self.retry_count = 0  # Reset retry count on successful output\\\\n\\\\n                    if not self.monitor.processing_input.is_set():\\\\n                        self._check_for_errors(line, error_buffer)\\\\n                else:\\\\n                    self._check_idle_state()\\\\n\\\\n            else:\\\\n                self._check_idle_state()\\\\n\\\\n            if self.monitor.restart_requested.is_set() and not self.monitor.processing_input.is_set():\\\\n                self.monitor.perform_restart()\\\\n\\\\n    def _check_idle_state(self):\\\\n        current_time = time.time()\\\\n        time_since_last_output = current_time - self.last_output_time\\\\n        if (time_since_last_output > 5 and\\\\n            not self.idle_prompt_shown and\\\\n                not self.monitor.processing_input.is_set()):\\\\n            print_info("\nNo more tasks to auto-process. What can I do next?")\\\\n            self._show_options()\\\\n            self.idle_prompt_shown = True\\\\n\\\\n    def _show_options(self):\\\\n        print_info("\nAvailable actions:")\\\\n        print_info("1. Give a coding instruction to perform")\\\\n        print_info("2. Process an image (type 'vision')")\\\\n        print_info("3. Exit monitoring mode (type 'exit')")\\\\n        print_info("\nType your choice or command:")\\\\n        print("> ", end="", flush=True)