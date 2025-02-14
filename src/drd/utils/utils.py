import click
from colorama import Fore, Style, Back
import json
import os

METADATA_FILE = 'drd.json'

def print_error(message):
    click.echo(f"{Fore.RED}✘ Error: {message}{Style.RESET_ALL}")

def print_success(message):
    click.echo(f"{Fore.GREEN}✔ Success: {message}{Style.RESET_ALL}")

def print_info(message):
    click.echo(f"{Fore.YELLOW}ℹ Info: {message}{Style.RESET_ALL}")

def print_warning(message):
    click.echo(f"{Fore.YELLOW}⚠ Warning: {message}{Style.RESET_ALL}")

def print_debug(message):
    click.echo(click.style(f"DEBUG: {message}", fg="cyan"))

def print_step(step_number, total_steps, message):
    click.echo(f"{Fore.CYAN}[{step_number}/{total_steps}] {message}{Style.RESET_ALL}")

def create_confirmation_box(message, action):
    box_width = len(message) + 4
    box_top = f"╔{'═' * box_width}╗"
    box_bottom = f"╚{'═' * box_width}╝"
    box_content = f"║  {message}  ║"

    confirmation_box = f"""\n{Fore.YELLOW}{box_top}\n║  {Back.RED}{Fore.WHITE}CONFIRMATION REQUIRED{Style.RESET_ALL}{Fore.YELLOW}  ║\n{box_content}\n╠{'═' * box_width}╣\n║  Do you want to {action}?  ║\n{box_bottom}{Style.RESET_ALL}\n"""
    return confirmation_box

def print_command_details(commands):
    for index, cmd in enumerate(commands, start=1):
        cmd_type = cmd.get('type', 'Unknown')
        print_info(f"Command {index} - Type: {cmd_type}")

        if cmd_type == 'shell':
            print_info(f"  Command: {cmd.get('command', 'Not provided')}")
        elif cmd_type == 'explanation':
            print_info(f"  Explanation: {cmd.get('content', 'Not provided')}")
        elif cmd_type == 'file':
            print_file_command_details(cmd)
        elif cmd_type == 'metadata':
            print_metadata_command_details(cmd)
        else:
            print_warning(f"  Unknown command type: {cmd_type}")

def print_file_command_details(cmd):
    operation = cmd.get('operation', 'Not provided')
    filename = cmd.get('filename', 'Not provided')
    content_preview = cmd.get('content', 'Not provided')
    if len(content_preview) > 50:
        content_preview = content_preview[:50] + "..."
    print_info(f"  Operation: {operation}")
    print_info(f"  Filename: {filename}")
    print_info(f"  Content: {content_preview}")

def print_metadata_command_details(cmd):
    operation = cmd.get('operation', 'Not provided')
    print_info(f"  Operation: {operation}")
    if operation == 'UPDATE_DEV_SERVER':
        print_info(f"  Start Command: {cmd.get('start_command', 'Not provided')}")
        print_info(f"  Framework: {cmd.get('framework', 'Not provided')}")
        print_info(f"  Language: {cmd.get('language', 'Not provided')}")
    elif operation in ['UPDATE_FILE', 'UPDATE']:
        print_info(f"  Filename: {cmd.get('filename', 'Not provided')}")
        print_info(f"  Language: {cmd.get('language', 'Not provided')}")
        print_info(f"  Description: {cmd.get('description', 'Not provided')}")

# Additional error handling and clearer output messages can be added based on the rules provided