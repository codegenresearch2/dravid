import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info, print_error

def run_dev_server_with_monitoring(command: str):
    print_info("ðŸš€ Starting server monitor...")
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }
    current_dir = os.getcwd()
    monitor = DevServerMonitor(current_dir, error_handlers, command)

    try:
        monitor.start()
        print_info("Server monitor is up and running! Press Ctrl+C to stop.")
        while not monitor.should_stop.is_set():
            pass
        print_info("Server monitor has ended.")
    except KeyboardInterrupt:
        print_info("Stopping server...")
    finally:
        monitor.stop()

def handle_module_not_found(error_msg, monitor):
    match = re.search(
        r"(?:Cannot find module|Module not found|ImportError|No module named).*['\"](.*?)['\"]", error_msg, re.IGNORECASE)
    if match:
        module_name = match.group(1)
        error = ImportError(f"Oops! It seems like the module '{module_name}' is missing. Please install it and try again.")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)

def handle_syntax_error(error_msg, monitor):
    error = SyntaxError(f"Uh-oh! There's a syntax error in your code. Please check for any missing or misplaced characters: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)

def handle_general_error(error_msg, monitor):
    error = Exception(f"Whoops! A general error has occurred. Here's what we know: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)