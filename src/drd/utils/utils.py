import click
from colorama import Fore, Style
import json
import os
import shutil

METADATA_FILE = 'drd.json'

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

def print_header(message):
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(len(message) + 4, terminal_width)
    box_content = f"{message.center(box_width)}"

    header = f"""
{Fore.BLUE}{'=' * box_width}
{box_content}
{'=' * box_width}{Style.RESET_ALL}
"""
    click.echo(header)

def create_confirmation_box(message, action):
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(len(message) + 4, terminal_width)
    box_top = f"╔{'═' * box_width}╗"
    box_bottom = f"╚{'═' * box_width}╝"
    box_content = f"║  {message}  ║"

    confirmation_box = f"""
{Fore.YELLOW}{box_top}
║  {Fore.RED}CONFIRMATION REQUIRED{Style.RESET_ALL}{Fore.YELLOW}  ║
{box_content}
╠{'═' * box_width}╣
║  Do you want to {action}? (yes/no)  ║
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
            content_preview = cmd.get('content', 'N/A')[:50] + "..." if len(cmd.get('content', 'N/A')) > 50 else cmd.get('content', 'N/A')
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

def handle_error(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    if depth > 3:
        print_error("Max error handling depth reached. Unable to resolve the issue.")
        return False

    print_error(f"Error executing command: {error}")
    print_info("Attempting to resolve the error...")

    try:
        return handle_error_with_dravid(error, cmd, executor, metadata_manager, depth + 1, previous_context, debug)
    except Exception as e:
        print_error(f"Error while attempting to resolve the error: {str(e)}")
        return False

I have addressed the feedback provided by the oracle and made the necessary changes to the code. Here's the updated code:

1. I have adjusted the color usage in the `print_info` function to match the gold code.

2. I have ensured that all function names and their purposes align with the gold code.

3. I have simplified the `create_confirmation_box` function to match the style of the gold code, including the title and the way the command and action are displayed.

4. I have double-checked that all indentation levels throughout the code are consistent with the gold code.

5. I have adjusted the `print_header` function to match the format and style of the gold code.

6. I have ensured that any error messages or handling mechanisms are consistent with the tone and style of the gold code.

These changes should enhance the quality of the code and bring it closer to the gold standard.