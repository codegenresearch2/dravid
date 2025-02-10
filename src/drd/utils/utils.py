import click
from colorama import Fore, Style, Back
import shutil
import json
import os

METADATA_FILE = 'drd.json'

def print_header(message):
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(len(message) + 4, terminal_width)
    box_top = f"╔{'═' * box_width}╗"
    box_bottom = f"╚{'═' * box_width}╝"
    box_content = f"║{' ' * ((box_width - len(message)) // 2)}{message}{' ' * ((box_width - len(message) + 1) // 2)}║"

    header_box = f"""
{Fore.BLUE}{box_top}
{box_content}
{box_bottom}{Style.RESET_ALL}
"""
    click.echo(header_box)

def print_error(message):
    click.echo(f"{Fore.RED}✘ {message}{Style.RESET_ALL}")

def print_success(message):
    click.echo(f"{Fore.GREEN}✔ {message}{Style.RESET_ALL}")

def print_prompt(message, indent=0):
    click.echo(f"{' ' * indent}{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    click.echo(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def print_debug(message):
    click.echo(click.style(f"DEBUG: {message}", fg="cyan"))

def print_step(step_number, total_steps, message):
    click.echo(f"{Fore.CYAN}[{step_number}/{total_steps}] {message}{Style.RESET_ALL}")

def create_confirmation_box(message, action):
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(len(message) + 4, terminal_width)
    box_top = f"╔{'═' * box_width}╗"
    box_bottom = f"╚{'═' * box_width}╝"
    box_content = f"║{' ' * ((box_width - len(message)) // 2)}{message}{' ' * ((box_width - len(message) + 1) // 2)}║"

    confirmation_box = f"""
{Fore.YELLOW}{box_top}
║  {Back.RED}{Fore.WHITE}CONFIRMATION REQUIRED{Style.RESET_ALL}{Fore.YELLOW}  ║
{box_content}
╠{'═' * box_width}╣
║{' ' * ((box_width - len(action)) // 2)}{action}{' ' * ((box_width - len(action) + 1) // 2)}║
{box_bottom}{Style.RESET_ALL}
"""
    return confirmation_box

def print_command_details(commands):
    for index, cmd in enumerate(commands, start=1):
        cmd_type = cmd.get('type', 'Unknown')
        print_prompt(f"Command {index} - Type: {cmd_type}")

        if cmd_type == 'shell':
            print_prompt(f"  Command: {cmd.get('command', 'N/A')}", indent=2)
        elif cmd_type == 'explanation':
            print_prompt(f"  Explanation: {cmd.get('content', 'N/A')}", indent=2)
        elif cmd_type == 'file':
            operation = cmd.get('operation', 'N/A')
            filename = cmd.get('filename', 'N/A')
            content_preview = cmd.get('content', 'N/A')
            if len(content_preview) > 50:
                content_preview = content_preview[:50] + "..."
            print_prompt(f"  Operation: {operation}", indent=2)
            print_prompt(f"  Filename: {filename}", indent=2)
            print_prompt(f"  Content: {content_preview}", indent=2)
        elif cmd_type == 'metadata':
            operation = cmd.get('operation', 'N/A')
            print_prompt(f"  Operation: {operation}", indent=2)
            if operation == 'UPDATE_DEV_SERVER':
                print_prompt(f"  Start Command: {cmd.get('start_command', 'N/A')}", indent=4)
                print_prompt(f"  Framework: {cmd.get('framework', 'N/A')}", indent=4)
                print_prompt(f"  Language: {cmd.get('language', 'N/A')}", indent=4)
            elif operation in ['UPDATE_FILE', 'UPDATE']:
                print_prompt(f"  Filename: {cmd.get('filename', 'N/A')}", indent=4)
                print_prompt(f"  Language: {cmd.get('language', 'N/A')}", indent=4)
                print_prompt(f"  Description: {cmd.get('description', 'N/A')}", indent=4)
        else:
            print_warning(f"  Unknown command type: {cmd_type}")

I have made the following changes to address the feedback:

1. Renamed `print_info` to `print_prompt` to align with the gold code's naming convention.
2. Changed the color used in `print_prompt` to blue to match the gold code.
3. Implemented the use of `shutil.get_terminal_size()` in the `create_confirmation_box` function to dynamically adjust the box width based on the terminal size.
4. Revised the box creation logic in `create_confirmation_box` to achieve a more structured layout with centered titles and commands.
5. Added the `print_header` function to provide a header output style.
6. Ensured consistent indentation levels in the `print_command_details` function.

These changes should help align your code more closely with the gold code and address the issues raised in the feedback.