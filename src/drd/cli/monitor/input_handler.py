import threading
import click
import os
import glob
import re
from ...utils import print_info, print_error, print_debug
from ...prompts.instructions import get_instruction_prompt
from ..query.main import execute_dravid_command

class InputHandler:
    def __init__(self, monitor):
        self.monitor = monitor
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._handle_input, daemon=True)
        self.thread.start()

    def _handle_input(self):
        while not self.monitor.should_stop.is_set():
            user_input = input("> ").strip()
            if user_input.lower() == 'exit':
                print_info("Exiting server monitor. Type 'exit' to confirm.")
                user_input = input("> ").strip()
                if user_input.lower() == 'exit':
                    self.monitor.stop()
                    break
            elif user_input.lower() == 'p':
                print_info("Initiating vision input. Use Tab for autocomplete.")
                self._handle_vision_input()
            else:
                print_info("Processing general input.")
                self._process_input(user_input)

    def _process_input(self, user_input):
        self.monitor.processing_input.set()
        try:
            self._handle_general_input(user_input)
        finally:
            self.monitor.processing_input.clear()

    def _handle_vision_input(self):
        user_input = self._get_input_with_autocomplete()
        self._handle_general_input(user_input)

    def _handle_general_input(self, user_input):
        image_path = self._extract_image_path(user_input)
        instructions = self._extract_instructions(user_input, image_path)
        instruction_prompt = get_instruction_prompt()

        if image_path and not os.path.exists(image_path):
            print_error(f"Image file not found: {image_path}")
            return

        try:
            print_info(f"Processing input: {user_input}")
            execute_dravid_command(instructions, image_path, False, instruction_prompt, warn=False)
        except Exception as e:
            print_error(f"Error processing input: {str(e)}")

    def _extract_image_path(self, user_input):
        image_pattern = r"([a-zA-Z0-9._/-]+(?:/|\\)?)+\.(jpg|jpeg|png|bmp|gif)"
        match = re.search(image_pattern, user_input)
        if match:
            return os.path.expanduser(match.group(0))
        return None

    def _extract_instructions(self, user_input, image_path):
        if image_path:
            return user_input.replace(image_path, "").strip()
        return user_input

    def _get_input_with_autocomplete(self):
        current_input = ""
        while True:
            char = click.getchar()
            if char == '\r':  # Enter key
                print()  # Move to next line
                return current_input
            elif char == '\t':  # Tab key
                completions = self._autocomplete(current_input)
                if len(completions) == 1:
                    current_input = completions[0]
                    click.echo("\r> " + current_input, nl=False)
                elif len(completions) > 1:
                    click.echo("\nPossible completions:")
                    for comp in completions:
                        click.echo(comp)
                    click.echo("> " + current_input, nl=False)
            elif char.isprintable():
                current_input += char
                click.echo(char, nl=False)
            elif char == '\x7f':  # Backspace
                if current_input:
                    current_input = current_input[:-1]
                    click.echo("\b \b", nl=False)

    def _autocomplete(self, text):
        path = os.path.expanduser(text)
        if os.path.isdir(path):
            path = os.path.join(path, '*')
        else:
            path = path + '*'

        completions = glob.glob(path)
        if len(completions) == 1 and os.path.isdir(completions[0]):
            return [completions[0] + os.path.sep]
        return completions