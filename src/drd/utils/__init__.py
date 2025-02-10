from .utils import (
    print_error,
    print_success,
    print_info,
    print_step,
    print_debug,
    print_warning,
    print_header,
    print_prompt,
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
    'run_with_loader',
    'print_header',
    'print_prompt',
]

I have addressed the feedback by removing any comments that might have been causing a syntax error in the `src/drd/utils/__init__.py` file. The code now only contains valid Python syntax, which should allow the tests to pass.