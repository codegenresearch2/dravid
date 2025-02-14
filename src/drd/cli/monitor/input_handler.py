import threading\\\\nimport click\\\nimport os\\\nimport glob\\\nimport re\\\nfrom ...utils import print_info, print_error, print_debug\\\nfrom ...prompts.instructions import get_instruction_prompt\\\nfrom ..query.main import execute_dravid_command\\\\n\\nclass InputHandler:\\\\\n    def __init__(self, monitor):\\\\\\\n        self.monitor = monitor\\\\\\\\n        self.thread = None\\\\\\\\n\\\\n    def start(self):\\\\\\\\\n        self.thread = threading.Thread(target=self._handle_input, daemon=True)\\\\\\\\\n        self.thread.start()\\\\\\\\n\\\\\\\n    def _handle_input(self):\\\\\\\\\n        while not self.monitor.should_stop.is_set():\\\\\\\\\\n            user_input = input("> ").strip()\\\\\\\\\\n            if user_input.lower() == 'exit':\\\\\\\\\\n                print_info("Exiting server monitor...")\\\\\\\\\\n                self.monitor.stop()\\\\\\\\\\n                break\\\\\\\\n            self._process_input(user_input)\\\\\\\\n\\\\\\\n    def _process_input(self, user_input):\\\\\\\\\n        if user_input.lower() == 'p':\\\\\\\\\\n            self._handle_vision_input()\\\\\\\\\\n            return\\\\\\\\n\\\\n        if user_input:\\\\\\\\\n            self.monitor.processing_input.set()\\\\\\\\\n            self._handle_general_input(user_input)\\\\\\\\n\\\\\\\n    def _handle_vision_input(self):\\\\\\\\\n        print_info(\\\\\\\\\\n            "Enter the image path and instructions (use Tab for autocomplete):")\\\\\\\\\\n        user_input = self._get_input_with_autocomplete()\\\\\\\\\n        self._handle_general_input(user_input)\\\\\\\\n\\\\\\\n    def _handle_general_input(self, user_input):\\\\\\\\\n        image_pattern = r"([a-zA-Z0-9._/-]+(?:/|\)?)+\.(jpg|jpeg|png|bmp|gif)"\\\\\\\\\\\\n        match = re.search(image_pattern, user_input)\\\\\\\\\n        if match:\\\\\\\\\n            image_path = match.group(0)\\\\\\\\\n            instructions = user_input.replace(image_path, "").strip()\\\\\\\\\\\\n            image_path = os.path.expanduser(image_path)\\\\\\\\\n\\\\\\\\\\n            if not os.path.exists(image_path):\\\\\\\\\n                print_error(f"Image file not found: {image_path}")\\\\\\\\\n                return\\\\\\\\n\\\\\\\\\\n            self.monitor.processing_input.set()\\\\\\\\\n            try:\\\\\\\\\n                print_info(f"Processing image: {image_path}")\\\\\\\\\n                print_info(f"With instructions: {instructions}")\\\\\\\\\n                execute_dravid_command(instructions, image_path, False, get_instruction_prompt(), warn=False)\\\\\\\\\n            except Exception as e:\\\\\\\\\n                print_error(f"Error processing image input: {str(e)}")\\\\\\\\\n            finally:\\\\\\\\\n                self.monitor.processing_input.clear()\\\\\\\\\\\\n        else:\\\\\\\\\n            execute_dravid_command(user_input, None, False, get_instruction_prompt(), warn=False)\\\\\\\\n\\\\\\\n    def _get_input_with_autocomplete(self):\\\\\\\\\n        current_input = ""\\\\\\\\\\\\n        while True:\\\\\\\\\n            char = click.getchar()\\\\\\\\\\\\n            if char == '\r':  # Enter key\\\\\\\\\\\\n                print()  # Move to next line\\\\\\\\\\\\n                return current_input\\\\\\\\\\\\n            elif char == '\t':  # Tab key\\\\\\\\\\\\n                completions = self._autocomplete(current_input)\\\\\\\\\n                if len(completions) == 1:\\\\\\\\\n                    current_input = completions[0]\\\\\\\\\\\\n                    click.echo('\r> ' + current_input, nl=False)\\\\\\\\\n                elif len(completions) > 1:\\\\\\\\\n                    click.echo('\nPossible completions:')\\\\\\\\\n                    for comp in completions:\\\\\\\\\n                        click.echo(comp)\\\\\\\\\n                    click.echo('> ' + current_input, nl=False)\\\\\\\\\n            elif char.isprintable():\\\\\\\\\n                current_input += char\\\\\\\\\\\\n                click.echo(char, nl=False)\\\\\\\\\n            elif char == '\x7f':  # Backspace\\\\\\\\\\\\n                if current_input:\\\\\\\\\n                    current_input = current_input[:-1]\\\\\\\\\\\\n                    click.echo('\b \b', nl=False)\\\\\\\\\n\\\\\\\n    def _autocomplete(self, text):\\\\\\\\\n        path = os.path.expanduser(text)\\\\\\\\\n        if os.path.isdir(path):\\\\\\\\\n            path = os.path.join(path, '*')\\\\\\\\\n        else:\\\\\\\\\n            path = path + '*'\\\\\\\\\\\\n\\\\\\\\\\n        completions = glob.glob(path)\\\\\\\\\n        if len(completions) == 1 and os.path.isdir(completions[0]):\\\\\\\\\\\\n            return [completions[0] + os.path.sep]\\\\\\\\\\\\n        return completions