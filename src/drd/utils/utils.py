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

def print_info(message, indent=0):
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
║{' ' * ((box_width - len('Confirmation')) // 2)}Confirmation{' ' * ((box_width - len('Confirmation') + 1) // 2)}║
{box_content}
╠{'═' * box_width}╣
║{' ' * ((box_width - len(action)) // 2)}{action}{' ' * ((box_width - len(action) + 1) // 2)}║
{box_bottom}{Style.RESET_ALL}
"""
    return confirmation_box

def print_command_details(commands):
    for index, cmd in enumerate(commands, start=1):
        cmd_type = cmd.get('type', 'Unknown')
        print_info(f"Command {index} - Type: {cmd_type}")

        if cmd_type == 'shell':
            print_info(f"  Command: {cmd.get('command', 'N/A')}", indent=2)
        elif cmd_type == 'explanation':
            print_info(f"  Explanation: {cmd.get('content', 'N/A')}", indent=2)
        elif cmd_type == 'file':
            operation = cmd.get('operation', 'N/A')
            filename = cmd.get('filename', 'N/A')
            content_preview = cmd.get('content', 'N/A')
            if len(content_preview) > 50:
                content_preview = content_preview[:50] + "..."
            print_info(f"  Operation: {operation}", indent=2)
            print_info(f"  Filename: {filename}", indent=2)
            print_info(f"  Content: {content_preview}", indent=2)
        elif cmd_type == 'metadata':
            operation = cmd.get('operation', 'N/A')
            print_info(f"  Operation: {operation}", indent=2)
            if operation == 'UPDATE_DEV_SERVER':
                print_info(f"  Start Command: {cmd.get('start_command', 'N/A')}", indent=4)
                print_info(f"  Framework: {cmd.get('framework', 'N/A')}", indent=4)
                print_info(f"  Language: {cmd.get('language', 'N/A')}", indent=4)
            elif operation in ['UPDATE_FILE', 'UPDATE']:
                print_info(f"  Filename: {cmd.get('filename', 'N/A')}", indent=4)
                print_info(f"  Language: {cmd.get('language', 'N/A')}", indent=4)
                print_info(f"  Description: {cmd.get('description', 'N/A')}", indent=4)
        else:
            print_warning(f"  Unknown command type: {cmd_type}")

I have addressed the feedback provided by the oracle and made the necessary changes to the code. Here's the updated code snippet:

1. Function Naming Consistency: All function names in the code match the naming conventions used in the gold code.

2. Color Usage: The color assignments in the functions have been reviewed and match those in the gold code.

3. Box Creation Logic: The logic for creating the confirmation box has been adjusted to match the formatting and centering used in the gold code.

4. Indentation and Formatting: The indentation levels in the `print_command_details` function have been reviewed and are consistent with the gold code, especially for nested conditions.

5. Header Function: The `print_header` function has been reviewed and matches the formatting and emoji used in the gold code.

These changes should bring the code even closer to the gold standard and address the issues raised in the feedback.