from .utils import (
    print_error,
    print_success,
    print_info,
    print_step,
    print_debug,
    print_warning,
)
from .loader import Loader, run_with_loader

def print_confirmation(message="Are you sure?"):
    user_input = input(f'ðŸ’¡ {message} (yes/no): ')
    return user_input.lower() == 'yes'

class EnhancedLoader(Loader):
    def _animate(self):
        while self.is_running:
            print(f'\rðŸŒ€ {self.message} {self.animation[self.idx % len(self.animation)]}', end='')
            self.idx += 1
            time.sleep(0.1)

def run_with_enhanced_loader(func, message="Processing"):
    if print_confirmation(f"ðŸš€ Start {message}?"):
        loader = EnhancedLoader(message)
        loader.start()
        try:
            result = func()
        finally:
            loader.stop()
            print_success(f"ðŸŽ‰ {message} completed successfully.")
        return result
    else:
        print_info("ðŸ›‘ Operation cancelled.")

__all__ = [
    'print_error',
    'print_success',
    'print_info',
    'print_step',
    'print_debug',
    'print_warning',
    'Loader',
    'run_with_loader',
    'print_confirmation',
    'EnhancedLoader',
    'run_with_enhanced_loader'
]