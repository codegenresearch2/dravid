import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info

def run_dev_server_with_monitoring(command: str):
    # Define error handlers for different types of errors
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }

    # Get the current working directory
    current_dir = os.getcwd()

    # Initialize the server monitor with the current directory, error handlers, and command
    monitor = DevServerMonitor(current_dir, error_handlers, command)

    try:
        # Start the server monitor
        monitor.start()
        print_info("ðŸš€ Server monitor is up and running! Press Ctrl+C to stop.")

        # Keep the program running until the server monitor is stopped
        while not monitor.should_stop.is_set():
            pass

        print_info("Server monitor has ended.")
    except KeyboardInterrupt:
        print_info("Stopping server...")
    finally:
        # Ensure the server monitor is stopped
        monitor.stop()

def handle_module_not_found(error_msg, monitor):
    # Handle module not found errors
    match = re.search(
        r"(?:Cannot find module|Module not found|ImportError|No module named).*['\"](.*?)['\"]", error_msg, re.IGNORECASE)
    if match:
        module_name = match.group(1)
        error = ImportError(f"Module '{module_name}' not found")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)

def handle_syntax_error(error_msg, monitor):
    # Handle syntax errors
    error = SyntaxError(f"Syntax error detected: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)

def handle_general_error(error_msg, monitor):
    # Handle general errors
    error = Exception(f"General error detected: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)