from .utils import (
    print_error,
    print_success,
    print_info,
    print_step,
    print_debug,
    print_warning,
    print_prompt,
    print_header
)
from .loader import Loader, run_with_loader

__all__ = [
    'print_error',
    'print_success',
    'print_info',
    'print_step',
    'print_debug',
    'print_warning',
    'print_prompt',
    'print_header',
    'Loader',
    'run_with_loader'
]


In the updated code, I have added `print_header` to the import statements from `.utils` and added it to the `__all__` list. This is to address the feedback from the oracle about including `print_header` for user-facing messages. The rest of the code remains the same.