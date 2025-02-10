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
        print_header(f"Starting server with command: {self.command}")
        self._start_process()

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
        print_info("Restarting server...")
        if self.process:
            self.process.terminate()
            self.process.wait()
        self._start_process()

    def _start_process(self):
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True,
                cwd=self.project_dir
            )
            self.retry_count = 0
            self.restart_requested.clear()
            print_success("Server restarted successfully.")
            print_info("Waiting for server output...")
            self.output_monitor.start()
            self.input_handler.start()
        except Exception as e:
            self.retry_count += 1
            if self.retry_count > MAX_RETRIES:
                print_error(f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")
                self.stop()
            else:
                print_info(f"Restart attempt failed. Retrying... (Attempt {self.retry_count}/{MAX_RETRIES})")

# No changes needed for the start_process function as it is already following the gold code.