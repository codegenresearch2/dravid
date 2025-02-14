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

# The code is already well-structured and modular, following the principles of maintainability and readability.
# However, we can add more descriptive docstrings for better understanding of the classes and functions.

# Updated Loader class with docstrings
class Loader:
    """\n    A class used to display a loading animation in the console.\n    It creates a new thread for the animation to run in parallel with the main program.\n    """

    def __init__(self, message="Processing"):
        """\n        Initialize the Loader with a custom message.\n\n        :param message: The message to display next to the loading animation.\n        """
        self.message = message
        self.is_running = False
        self.animation = "|/-\\"
        self.idx = 0
        self.thread = None

    def start(self):
        """\n        Start the loading animation in a new thread.\n        """
        self.is_running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.start()

    def stop(self):
        """\n        Stop the loading animation and clear the line.\n        """
        self.is_running = False
        if self.thread:
            self.thread.join()
        click.echo('\r' + ' ' * (len(self.message) + 10), nl=False)
        click.echo('\r', nl=False)

    def _animate(self):
        """\n        Display the loading animation.\n        """
        while self.is_running:
            click.echo(
                f'\r{self.message} {self.animation[self.idx % len(self.animation)]}', nl=False)
            self.idx += 1
            time.sleep(0.1)

# Updated run_with_loader function with docstrings
def run_with_loader(func, message="Processing"):
    """\n    Run a function with a loading animation in the console.\n\n    :param func: The function to run.\n    :param message: The message to display next to the loading animation.\n    :return: The result of the function.\n    """
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
        print_success("Processing completed successfully.")
    return result

I have rewritten the code according to the provided rules. I have added docstrings to the `Loader` class and the `run_with_loader` function for better understanding of their functionality. Additionally, I have improved the error handling in the `run_with_loader` function by catching any exceptions that might be raised during the execution of the function. In case of an exception, the loader is stopped, an error message is printed, and the exception is re-raised. If no exceptions are raised, the loader is stopped and a success message is printed.