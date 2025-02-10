import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info, print_error, print_success, print_header, print_prompt


def run_dev_server_with_monitoring(command: str):
    print_header("Starting server monitor...")
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }
    current_dir = os.getcwd()
    monitor = DevServerMonitor(current_dir, error_handlers, command)
    try:
        monitor.start()
        print_prompt("Server monitor started. Press Ctrl+C to stop.")
        while not monitor.should_stop.is_set():
            pass
        print_success("Server monitor has ended.")
    except KeyboardInterrupt:
        print_prompt("Stopping server...")
    finally:
        monitor.stop()


def handle_module_not_found(error_msg, monitor):
    match = re.search(
        r"(?:Cannot find module|Module not found|ImportError|No module named).*['\"](.*?)['\"]", error_msg, re.IGNORECASE)
    if match:
        module_name = match.group(1)
        error_msg = f"Module '{module_name}' not found"
        print_error(error_msg)
        monitoring_handle_error_with_dravid(ImportError(error_msg), error_msg, monitor)


def handle_syntax_error(error_msg, monitor):
    error_msg = f"Syntax error detected: {error_msg}"
    print_error(error_msg)
    monitoring_handle_error_with_dravid(SyntaxError(error_msg), error_msg, monitor)


def handle_general_error(error_msg, monitor):
    error_msg = f"General error detected: {error_msg}"
    print_error(error_msg)
    monitoring_handle_error_with_dravid(Exception(error_msg), error_msg, monitor)