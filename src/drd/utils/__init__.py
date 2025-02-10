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

# Rewritten code with enhanced visual feedback and consistent indentation
def print_confirmation(message="Are you sure? ðŸ¤”"):
    user_input = input(f'\r{message} (yes/no): ')
    return user_input.lower() == 'yes'

def print_processing(message="Processing ðŸš€"):
    loader = Loader(message)
    loader.start()
    try:
        result = yield
    finally:
        loader.stop()
    return result


In the rewritten code, I added two new functions: `print_confirmation` and `print_processing`. The `print_confirmation` function prompts the user with a custom message and returns `True` if the user inputs 'yes', and `False` otherwise. The `print_processing` function uses the `Loader` class to display a processing animation with a custom message. It uses a generator to allow the caller to yield a result while the loader is running.