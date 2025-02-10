from .utils import (
    print_error,
    print_success,
    print_info,
    print_step,
    print_debug,
    print_warning,
)
from .loader import Loader, run_with_loader

__all__ = [
    'print_error',
    'print_success',
    'print_info',
    'print_step',
    'print_debug',
    'print_warning',
    'Loader',
    'run_with_loader'
]

# The code snippet is already well-structured and readable. However, to improve error handling and user feedback,
# we can add more specific error messages and handle exceptions in the run_with_loader function.

def run_with_loader(func, message="Processing"):
    loader = Loader(message)
    loader.start()
    try:
        result = func()
    except Exception as e:
        loader.stop()
        print_error(f"An error occurred: {str(e)}")
        raise
    else:
        loader.stop()
        print_success(f"{message} completed successfully.")
    return result