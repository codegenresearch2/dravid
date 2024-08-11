import sys
import click
from colorama import Fore, Style


def confirm_with_user(msg):
    return click.confirm(f"{Fore.YELLOW} {msg} {Style.RESET_ALL}", default=False)


def get_user_confirmation(msg):
    return click.confirm(f"{Fore.YELLOW} {msg} {Style.RESET_ALL}", default=False)


def get_input_with_timeout(msg, timeout):
    try:
        return click.prompt(
            msg,
            type=str,
            default='',
            show_default=False,
            prompt_suffix=''
        )
    except click.exceptions.Abort:
        print("\nInput timeout reached.")
        return None
