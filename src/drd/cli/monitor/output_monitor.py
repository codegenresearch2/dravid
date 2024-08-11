import logging
import sys
import select
import time
import threading
from collections import deque
from .state import ServerState
import re

logger = logging.getLogger(__name__)


class OutputMonitor:
    def __init__(self, monitor):
        self.monitor = monitor
        self.thread = None
        self.last_output_time = None
        self.idle_detected = threading.Event()
        self.stop_event = threading.Event()
        self.buffer_size = 50  # Number of lines to keep in buffer
        self.error_timeout = 2
        logger.info("OutputMonitor initialized")

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._monitor_output, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)

    def _monitor_output(self):
        output_buffer = deque(maxlen=self.buffer_size)
        self.last_output_time = time.time()
        error_detected = False
        error_start_time = None

        logger.info("Starting output monitoring")
        while not self.stop_event.is_set():
            if self.monitor.get_state() != ServerState.NORMAL:
                time.sleep(0.1)  # Small sleep when not in normal state
                continue
            if self.monitor.process is None or self.monitor.process.poll() is not None:
                logger.info(
                    "Server process ended or not started. Waiting for restart...")
                time.sleep(1)
                continue

            try:
                ready, _, _ = select.select(
                    [self.monitor.process.stdout], [], [], 0.1)
                if self.monitor.process.stdout in ready:
                    line = self.monitor.process.stdout.readline()
                    if line:
                        line = line.strip()
                        print(line, flush=True)
                        sys.stdout.flush()
                        output_buffer.append(line)

                        self.last_output_time = time.time()
                        self.monitor.retry_count = 0

                        if not error_detected:
                            error_detected = self._check_for_errors(line)
                            if error_detected:
                                error_start_time = time.time()
                        elif time.time() - error_start_time > self.error_timeout:
                            self._handle_error(list(output_buffer))
                            error_detected = False
                            output_buffer.clear()
                    else:
                        self._check_idle_state()
                else:
                    self._check_idle_state()

                if error_detected and time.time() - error_start_time > self.error_timeout:
                    self._handle_error(list(output_buffer))
                    error_detected = False
                    output_buffer.clear()

            except Exception as e:
                logger.error(f"Error in output monitoring: {str(e)}")
                time.sleep(1)  # Prevent rapid error logging

        logger.info("Output monitoring stopped.")

    def _check_for_errors(self, line):
        logger.info(f"Checking for errors in line: {line}")
        for error_pattern in self.monitor.error_handlers.keys():
            if re.search(error_pattern, line, re.IGNORECASE):
                return True
        return False

    def _handle_error(self, error_context):
        self.monitor.set_state(ServerState.ERROR_DETECTED)
        full_error = '\n'.join(error_context)
        self.monitor.handle_error(full_error)

    def _check_idle_state(self):
        current_time = time.time()
        if (current_time - self.last_output_time > 5 and
                not self.monitor.error_handling_in_progress.is_set() and
                not self.monitor.processing_input.is_set()):
            self.idle_detected.set()
            logger.info("Idle state detected")
