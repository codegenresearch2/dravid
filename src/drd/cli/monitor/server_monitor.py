import sys
import time
import re
import threading
from threading import Lock
import subprocess
from queue import Queue
from .input_handler import InputHandler
from .output_monitor import OutputMonitor
from ...utils import print_info, print_success, print_error, print_header, print_prompt, print_warning
from ...metadata.project_metadata import ProjectMetadataManager
from ...utils.input import get_user_confirmation
from .state import ServerState
from .history_tracker import HistoryTracker, EventType

import logging


logger = logging.getLogger(__name__)


class DevServerMonitor:
    def __init__(self, project_dir: str, error_handlers: dict, command: str, default_handler: any):
        self.project_dir = project_dir
        self.MAX_RETRIES = 3
        self.error_handlers = error_handlers
        self.command = command
        self.error_context = ""
        self.error_handler = None
        self.process = None
        self.should_stop = threading.Event()
        self.restart_requested = threading.Event()
        self.processing_input = threading.Event()
        self.skip_input = False
        self.input_handler = InputHandler(self)
        self.output_monitor = OutputMonitor(self)
        self.retry_count = 0
        self.metadata_manager = ProjectMetadataManager(project_dir)
        self.error_handling_in_progress = threading.Event()
        self.error_handlers = {
            str(pattern): handler for pattern, handler in error_handlers.items()

        }
        self.error_handlers['default'] = default_handler
        self.state = ServerState.NORMAL
        self.history_tracker = HistoryTracker(max_entries=5)
        self.state_lock = Lock()
        logger.info(
            f"Initialized error handlers: {list(self.error_handlers.keys())}")

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
                current_state = self.get_state()
                if current_state == ServerState.NORMAL:
                    if self.output_monitor.idle_detected.is_set():
                        self.input_handler.handle_input()
                        self.output_monitor.idle_detected.clear()
                elif current_state == ServerState.ERROR_DETECTED:
                    pass
                elif current_state == ServerState.ERROR_HANDLING:
                    # Wait for error handling to complete
                    pass
                elif current_state == ServerState.FIX_APPLYING:
                    # Wait for fix to be applied
                    pass

                # Small sleep to prevent busy waiting
                self.should_stop.wait(timeout=0.1)
        except KeyboardInterrupt:
            logger.info("Stopping server...")
        finally:
            self.stop()

    def resume_error_handling(self, user_input, skip=False):
        if user_input.lower() == 'y' and self.get_state() == ServerState.ERROR_HANDLING:
            self.set_state(ServerState.FIX_APPLYING)
            self.error_handler(self.error_context, self)
            logger.info("CLEANING UP....")
            error_message = f"Error detected: {self.error_context[:300]}... Fix it"
            self.history_tracker.add_event(EventType.USER, error_message)
            self.clean_handlers()

    def clean_handlers(self):
        self.error_context = ""
        self.error_handler = None
        self.set_state(ServerState.NORMAL)

    def handle_error(self, error_context):
        logger.info("Entering handle_error method")
        self.set_state(ServerState.ERROR_HANDLING)
        self.output_monitor.idle_detected.clear()

        # print_warning("An error has been detected. Here's the context:")
        sys.stdout.flush()  # Ensure immediate flushing
        # Wait a short time to ensure all output is flushed
        time.sleep(0.1)

        try:
            for pattern, handler in self.error_handlers.items():
                logger.info(f"Checking error pattern: {pattern}")
                if re.search(pattern, error_context, re.IGNORECASE):
                    logger.info(f"Matched error pattern: {pattern}")
                    self.error_context = error_context
                    self.error_handler = handler
                    if not get_user_confirmation("Do you want to proceed with the fix from Dravid?"):
                        self.clean_handlers()
                        return True

                    self.resume_error_handling('y')
                    break
            else:
                logger.warning(
                    "No specific handler found for this error. Using default error handler.")
                print_warning(
                    "No specific handler found for this error. Using default error handler.")
                self.error_handlers['default'](error_context, self)
        except Exception as e:
            logger.error(f"Error during error handling: {str(e)}")
            print_error(f"Failed to handle the error: {str(e)}")

        self.clean_handlers()
        logger.info("Exiting handle_error method")

    def request_restart(self):
        self.restart_requested.set()

    def set_state(self, new_state: ServerState):
        with self.state_lock:
            self.state = new_state
            logger.info(f"Server state changed to: {self.state.name}")

    def get_state(self) -> ServerState:
        with self.state_lock:
            return self.state
