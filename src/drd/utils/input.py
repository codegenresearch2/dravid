import sys
import click
from colorama import Fore, Style


def confirm_with_user(msg):
    return click.confirm(f"{Fore.YELLOW} {msg} {Style.RESET_ALL}", default=False)


def get_user_confirmation(prompt):
    sys.stdout.write(f"{prompt} [y/N] ")
    sys.stdout.flush()
    user_input = input().strip().lower()
    if user_input in ['y', 'yes']:
        return True
    elif user_input in ['', 'n', 'no']:
        return False
    else:
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")
