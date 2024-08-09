import logging
import select
import time
import threading
import re

logger = logging.getLogger(__name__)


class OutputMonitor:
    def __init__(self, monitor):
        self.monitor = monitor
        self.thread = None
        self.last_output_time = None
        self.idle_detected = threading.Event()
        self.stop_event = threading.Event()

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
        error_buffer = []
        self.last_output_time = time.time()

        while not self.stop_event.is_set():
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
                        logger.debug(f"Server output: {line}")
                        error_buffer.append(line)
                        if len(error_buffer) > 10:
                            error_buffer.pop(0)
                        self.last_output_time = time.time()
                        self.monitor.retry_count = 0
                        if not self.monitor.processing_input.is_set():
                            self._check_for_errors(line, error_buffer)
                    else:
                        self._check_idle_state()
                else:
                    self._check_idle_state()
            except Exception as e:
                logger.error(f"Error in output monitoring: {str(e)}")
                time.sleep(1)  # Prevent rapid error logging

        logger.info("Output monitoring stopped.")

    def _check_for_errors(self, line, error_buffer):
        for error_pattern in self.monitor.error_handlers.keys():
            if re.search(error_pattern, line, re.IGNORECASE):
                full_error = '\n'.join(error_buffer)
                logger.error(f"Error detected: {full_error}")
                self.monitor.handle_error(full_error)
                error_buffer.clear()
                break

    def _check_idle_state(self):
        current_time = time.time()
        if (current_time - self.last_output_time > 5 and
                not self.monitor.error_handling_in_progress.is_set() and
                not self.monitor.processing_input.is_set()):
            self.idle_detected.set()
