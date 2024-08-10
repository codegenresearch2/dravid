import re
import threading
import subprocess
from queue import Queue
from .input_handler import InputHandler
from .output_monitor import OutputMonitor
from ...utils import print_info, print_success, print_error, print_header, print_prompt
from ...metadata.project_metadata import ProjectMetadataManager

import logging


logger = logging.getLogger(__name__)


class DevServerMonitor:
    def __init__(self, project_dir: str, error_handlers: dict, command: str):
        self.project_dir = project_dir
        self.MAX_RETRIES = 3
        self.error_handlers = error_handlers
        self.command = command
        self.process = None
        self.should_stop = threading.Event()
        self.restart_requested = threading.Event()
        self.processing_input = threading.Event()
        self.input_handler = InputHandler(self)
        self.output_monitor = OutputMonitor(self)
        self.retry_count = 0
        self.metadata_manager = ProjectMetadataManager(project_dir)
        self.error_handling_in_progress = threading.Event()
        self.error_handlers = {
            str(pattern): handler for pattern, handler in error_handlers.items()
        }

    def start(self):
        self.should_stop.clear()
        self.restart_requested.clear()
        logger.info(f"Starting server with command: {self.command}")
        try:
            self.process = self.start_process()
            self.output_monitor.start()
            self._main_loop()
        except Exception as e:
            logger.error(f"Failed to start server process: {str(e)}")
            self.stop()

    def stop(self):
        logger.info("Stopping server monitor...")
        self.should_stop.set()
        self.output_monitor.stop()
        if self.process:
            logger.info("Terminating server process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate, forcing...")
                self.process.kill()
        logger.info("Server monitor stopped.")

    def perform_restart(self):
        logger.info("Restarting server...")
        if self.process:
            logger.info("Terminating existing process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate, forcing...")
                self.process.kill()

        try:
            logger.info(f"Starting new process with command: {self.command}")
            self.start()
            logger.info("Server restart completed.")
            print("Server restarted successfully. Waiting for output...")
        except Exception as e:
            logger.error(f"Failed to restart server process: {str(e)}")
            print(f"Failed to restart server process: {str(e)}")
            self.retry_count += 1
            if self.retry_count >= self.MAX_RETRIES:
                logger.error(
                    f"Server failed to start after {self.MAX_RETRIES} attempts. Exiting.")
                print(
                    f"Server failed to start after {self.MAX_RETRIES} attempts. Exiting.")
                self.stop()
            else:
                logger.info(
                    f"Retrying... (Attempt {self.retry_count + 1}/{self.MAX_RETRIES})")
                print(
                    f"Retrying... (Attempt {self.retry_count + 1}/{self.MAX_RETRIES})")
                self.request_restart()

    def start_process(self):
        return subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=True,
            cwd=self.project_dir
        )

    def _main_loop(self):
        try:
            while not self.should_stop.is_set():
                if self.error_handling_in_progress.is_set():
                    # Wait for error handling to complete
                    self.error_handling_in_progress.wait()
                elif self.output_monitor.idle_detected.is_set():
                    self.input_handler.handle_input()
                    self.output_monitor.idle_detected.clear()
                else:
                    # Small sleep to prevent busy waiting
                    self.should_stop.wait(timeout=0.1)
        except KeyboardInterrupt:
            print_info("Stopping server...")
        finally:
            self.stop()

    def handle_error(self, error_msg):
        self.error_handling_in_progress.set()
        self.output_monitor.idle_detected.clear()
        try:
            for pattern, handler in self.error_handlers.items():
                if re.search(pattern, error_msg, re.IGNORECASE):
                    handler(error_msg, self)
                    break
        finally:
            self.error_handling_in_progress.clear()

    def request_restart(self):
        self.restart_requested.set()
