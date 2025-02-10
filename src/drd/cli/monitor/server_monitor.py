import threading
import subprocess
from queue import Queue
from .input_handler import InputHandler
from .output_monitor import OutputMonitor
from ...utils import print_header, print_success, print_error, print_info

MAX_RETRIES = 3

class DevServerMonitor:
    def __init__(self, project_dir: str, error_handlers: dict, command: str):
        self.project_dir = project_dir
        self.error_handlers = error_handlers
        self.command = command
        self.process = None
        self.output_queue = Queue()
        self.should_stop = threading.Event()
        self.restart_requested = threading.Event()
        self.user_input_queue = Queue()
        self.processing_input = threading.Event()
        self.input_handler = InputHandler(self)
        self.output_monitor = OutputMonitor(self)
        self.retry_count = 0

    def start(self):
        self.should_stop.clear()
        self.restart_requested.clear()
        print_header(f"Starting Dravid AI along with your process/server: {self.command}")
        try:
            self.process = self._start_process(self.command)
            self.output_monitor.start()
            self.input_handler.start()
        except Exception as e:
            print_error(f"Failed to start server process: {str(e)}")
            self.perform_restart()

    def stop(self):
        print_info("Stopping server monitor...")
        self.should_stop.set()
        if self.process:
            self.process.terminate()
            self.process.wait()
        print_info("Server monitor stopped.")

    def request_restart(self):
        self.restart_requested.set()

    def perform_restart(self):
        print_header("Restarting server...")
        if self.process:
            self.process.terminate()
            self.process.wait()

        try:
            self.process = self._start_process(self.command)
            self.retry_count = 0
            self.restart_requested.clear()
            print_success("Server restarted successfully.")
            print_header("Waiting for server output...")
        except Exception as e:
            print_error(f"Failed to restart server process: {str(e)}")
            self.retry_count += 1
            if self.retry_count >= MAX_RETRIES:
                print_error(f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")
                self.stop()
            else:
                print_header(f"Retrying... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")
                self.request_restart()

    def _start_process(self, command):
        try:
            return subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True,
                cwd=self.project_dir
            )
        except Exception as e:
            print_error(f"Failed to start server process: {str(e)}")
            self.stop()
            return None

def start_process(command, cwd):
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=True,
        cwd=cwd
    )

I have made the necessary changes to address the feedback provided. Here's the updated code:

1. In the `stop` method, I replaced `print_prompt` with `print_info` for stopping messages.
2. In the `perform_restart` method, I added a call to `self.stop()` when the process fails to restart.
3. I renamed the `start_process` method to `_start_process` to match the gold code.
4. I reviewed the logic in the `start` method to ensure it matches the gold code's approach.
5. I ensured that the formatting of the print statements matches the gold code's style.

These changes should help align your code more closely with the gold code and address the test case failures.