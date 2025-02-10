import threading
import subprocess
from queue import Queue
from .input_handler import InputHandler
from .output_monitor import OutputMonitor
from ...utils import print_header, print_success, print_error

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
        print_header("Starting server with command: {}".format(self.command))
        try:
            self.process = self._start_process(self.command)
            self.output_monitor.start()
            self.input_handler.start()
        except Exception as e:
            print_error("Failed to start server process: {}".format(str(e)))
            self.stop()

    def stop(self):
        print_header("Stopping server monitor...")
        self.should_stop.set()
        if self.process:
            self.process.terminate()
            self.process.wait()
        print_prompt("Server monitor stopped.")

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
            print_error("Failed to restart server process: {}".format(str(e)))
            self.retry_count += 1
            if self.retry_count >= MAX_RETRIES:
                print_error(
                    "Server failed to start after {} attempts. Exiting.".format(MAX_RETRIES))
                self.stop()
            else:
                print_header(
                    "Retrying... (Attempt {}/{})".format(self.retry_count + 1, MAX_RETRIES))
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
            print_error("Failed to start server process: {}".format(str(e)))
            self.stop()
            return None