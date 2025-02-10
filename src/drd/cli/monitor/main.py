import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info, print_error

def run_dev_server_with_monitoring(command: str):
    print_info("Initializing server monitor...")
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }
    current_dir = os.getcwd()
    monitor = DevServerMonitor(current_dir, error_handlers, command)

    try:
        monitor.start()
        print_info("Server monitor has been successfully started. Press Ctrl+C to stop.")
        while not monitor.should_stop.is_set():
            pass
        print_info("Server monitor has ended.")
    except KeyboardInterrupt:
        print_info("Stopping server...")
        monitor.stop()
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        monitor.stop()

def handle_module_not_found(error_msg, monitor):
    match = re.search(
        r"(?:Cannot find module|Module not found|ImportError|No module named).*['\"](.*?)['\"]", error_msg, re.IGNORECASE)
    if match:
        module_name = match.group(1)
        error = ImportError(f"Module '{module_name}' could not be found. Please ensure it is installed and imported correctly.")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)
    else:
        error = ImportError(f"A module could not be found. Please check the error message for more details: {error_msg}")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)

def handle_syntax_error(error_msg, monitor):
    error = SyntaxError(f"A syntax error has been detected. Please check your code for any missing or misplaced characters: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)

def handle_general_error(error_msg, monitor):
    error = Exception(f"A general error has been detected. Please check the error message for more details: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)