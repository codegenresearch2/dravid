import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt

def print_step(step, total_steps, message):
    # Implementation of print_step function
    print(f"ð Step {step}/{total_steps}: {message}")

def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"
        print_step(i, total_steps, f"Processing {cmd['type']} {step_description}...")

        if cmd['type'] == 'explanation':
            print_info(f"Explanation: {cmd['content']}")
            all_outputs.append(f"Step {i}/{total_steps}: Explanation - {cmd['content']}")
        else:
            try:
                if cmd['type'] == 'shell':
                    output = handle_shell_command(cmd, executor)
                elif cmd['type'] == 'file':
                    output = handle_file_operation(cmd, executor, metadata_manager)
                elif cmd['type'] == 'metadata':
                    output = handle_metadata_operation(cmd, metadata_manager)

                if isinstance(output, str) and output.startswith("Skipping"):
                    print_info(f"Step {i}/{total_steps}: {output}")
                    all_outputs.append(f"Step {i}/{total_steps}: {output}")
                else:
                    all_outputs.append(f"Step {i}/{total_steps}: {cmd['type'].capitalize()} command - {cmd.get('command', '')} {cmd.get('operation', '')}\nOutput: {output}")

            except Exception as e:
                error_message = f"Step {i}/{total_steps}: Error executing {step_description}: {cmd}\nError details: {str(e)}"
                print_error(error_message)
                all_outputs.append(error_message)
                return False, i, str(e), "\n".join(all_outputs)

        if debug:
            print_debug(f"Completed step {i}/{total_steps}")

    return True, total_steps, None, "\n".join(all_outputs)

# Rest of the code remains the same