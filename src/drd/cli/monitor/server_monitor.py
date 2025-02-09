import threading\\\\\nimport subprocess\\\\\nfrom queue import Queue\\\\\nfrom .input_handler import InputHandler\\\\\nfrom .output_monitor import OutputMonitor\\\\\nfrom ...utils import print_info, print_success, print_error, print_header, print_prompt\\\\\n\\\\\nMAX_RETRIES = 3\\\\\n\\\\\nclass DevServerMonitor:\\\\\n    def __init__(self, project_dir: str, error_handlers: dict, command: str):\\\\\n        self.project_dir = project_dir\\\\\n        self.error_handlers = error_handlers\\\\\n        self.command = command\\\\\n        self.process = None\\\\\n        self.output_queue = Queue()\\\\\n        self.should_stop = threading.Event()\\\\\n        self.restart_requested = threading.Event()\\\\\n        self.user_input_queue = Queue()\\\\\n        self.processing_input = threading.Event()\\\\\n        self.input_handler = InputHandler(self)\\\\\n        self.output_monitor = OutputMonitor(self)\\\\\n        self.retry_count = 0\\\\\n\\\\\n    def start(self):\\\\\n        self.should_stop.clear()\\\\\n        self.restart_requested.clear()\\\\\n        print_info(f"Starting server with command: {self.command}")\\\\\n        try:\\\\\n            self.process = self._start_process(self.command, self.project_dir)\\\\\n            self.output_monitor.start()\\\\\n            self.input_handler.start()\\\\\n        except Exception as e:\\\\\n            print_error(f"Failed to start server process: {str(e)}")\\\\\n            self.stop()\\\\\n\\\\\n    def stop(self):\\\\\n        print_info("Stopping server monitor...")\\\\\n        self.should_stop.set()\\\\\n        if self.process:\\\\\n            self.process.terminate()\\\\\n            self.process.wait()\\\\\n        print_info("Server monitor stopped.")\\\\\n\\\\\n    def request_restart(self):\\\\\n        self.restart_requested.set()\\\\\n\\\\\n    def perform_restart(self):\\\\\n        print_info("Restarting server...")\\\\\n        if self.process:\\\\\n            self.process.terminate()\\\\\n            self.process.wait()\\\\\n\\\\\n        try:\\\\\n            self.process = self._start_process(self.command, self.project_dir)\\\\\n            self.retry_count = 0\\\\\n            self.restart_requested.clear()\\\\\n            print_success("Server restarted successfully.")\\\\\n            print_info("Waiting for server output...")\\\\\n        except Exception as e:\\\\\n            print_error(f"Failed to restart server process: {str(e)}")\\\\\n            self.retry_count += 1\\\\\n            if self.retry_count >= MAX_RETRIES:\\\\\n                print_error(\\\\\n                    f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")\\\\\n                self.stop()\\\\\n            else:\\\\\n                print_info(\\\\\n                    f"Retrying... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")\\\\\n                self.request_restart()\\\\\n\\\\\n    def _start_process(self, command, cwd):\\\\\n        try:\\\\\n            return subprocess.Popen(\\\\\n                command,\\\\\n                stdout=subprocess.PIPE,\\\\\n                stderr=subprocess.STDOUT,\\\\\n                stdin=subprocess.PIPE,\\\\\n                text=True,\\\\\n                bufsize=1,\\\\\n                universal_newlines=True,\\\\\n                shell=True,\\\\\n                cwd=cwd\\\\\n            )\\\\\n        except Exception as e:\\\\\n            print_error(f"Failed to start server process: {str(e)}")\\\\\n            self.stop()\\\\\n            return None