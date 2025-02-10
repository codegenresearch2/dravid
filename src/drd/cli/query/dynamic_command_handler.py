import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_step, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt

def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"
        try:
            output = handle_command(i, total_steps, cmd, executor, metadata_manager)
            all_outputs.append(output)

            if debug:
                print_debug(f"Completed step {i}/{total_steps}")

        except Exception as e:
            error_message = format_error_message(i, total_steps, step_description, cmd, str(e))
            print_error(error_message)
            all_outputs.append(error_message)
            return False, i, str(e), "\n".join(all_outputs)

    return True, total_steps, None, "\n".join(all_outputs)

def handle_command(i, total_steps, cmd, executor, metadata_manager):
    output = ""
    if cmd['type'] == 'explanation':
        output = f"Step {i}/{total_steps}: Explanation - {cmd['content']}"
    elif cmd['type'] == 'shell':
        output = handle_shell_command(i, total_steps, cmd, executor)
    elif cmd['type'] == 'file':
        output = handle_file_operation(i, total_steps, cmd, executor, metadata_manager)
    elif cmd['type'] == 'metadata':
        output = handle_metadata_operation(i, total_steps, cmd, metadata_manager)
    elif cmd['type'] == 'requires_restart':
        output = f"Step {i}/{total_steps}: Requires restart - {cmd['content']}"
    else:
        raise ValueError(f"Unknown command type: {cmd['type']}")
    return output

def format_error_message(i, total_steps, step_description, cmd, error_details):
    return f"Step {i}/{total_steps}: Error executing {step_description}: {cmd}\nError details: {error_details}"

def handle_shell_command(i, total_steps, cmd, executor):
    output = executor.execute_shell_command(cmd['command'])
    if isinstance(output, str) and output.startswith("Skipping"):
        print_info(f"Step {i}/{total_steps}: {output}")
        return f"Step {i}/{total_steps}: Shell command - {cmd['command']}\nOutput: {output}"
    if output is None:
        output = "Command failed"
    return f"Step {i}/{total_steps}: Shell command - {cmd['command']}\nOutput: {output}"

def handle_file_operation(i, total_steps, cmd, executor, metadata_manager):
    operation_performed = executor.perform_file_operation(cmd['operation'], cmd['filename'], cmd.get('content'), force=True)
    if isinstance(operation_performed, str) and operation_performed.startswith("Skipping"):
        print_info(f"Step {i}/{total_steps}: {operation_performed}")
        return f"Step {i}/{total_steps}: File operation - {cmd['operation']} on {cmd['filename']}\nOutput: {operation_performed}"
    elif operation_performed:
        if cmd['operation'] in ['CREATE', 'UPDATE']:
            update_file_metadata(cmd, metadata_manager, executor)
        return f"Step {i}/{total_steps}: File operation - {cmd['operation']} on {cmd['filename']}\nOutput: Success"
    else:
        return f"Step {i}/{total_steps}: File operation - {cmd['operation']} on {cmd['filename']}\nOutput: Failed"

def handle_metadata_operation(i, total_steps, cmd, metadata_manager):
    if cmd['operation'] in ['CREATE', 'UPDATE']:
        update_file_metadata(cmd, metadata_manager)
        return f"Step {i}/{total_steps}: Metadata operation - {cmd['operation']} on {cmd['filename']}\nOutput: Success"
    else:
        return f"Step {i}/{total_steps}: Metadata operation - {cmd['operation']} on {cmd['filename']}\nOutput: Unknown operation"

def update_file_metadata(cmd, metadata_manager, executor):
    project_context = metadata_manager.get_project_context()
    folder_structure = executor.get_folder_structure()
    file_type, description, exports = generate_file_description(cmd['filename'], cmd.get('content', ''), project_context, folder_structure)
    metadata_manager.update_file_metadata(cmd['filename'], file_type, cmd.get('content', ''), description, exports)
    print_success(f"Updated metadata for file: {cmd['filename']}")

def handle_error_with_dravid(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    if depth > 3:
        print_error("Max error handling depth reached. Unable to resolve the issue.")
        return False

    print_error(f"Error executing command: {error}")

    error_message = str(error)
    error_type = type(error).__name__
    error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    project_context = metadata_manager.get_project_context()
    error_query = get_error_resolution_prompt(previous_context, cmd, error_type, error_message, error_trace, project_context)

    print_info("ðŸ Sending error information to dravid for analysis(1 LLM call)...\n")

    try:
        fix_commands = call_dravid_api(error_query, include_context=True)
    except ValueError as e:
        print_error(f"Error parsing dravid's response: {str(e)}")
        return False

    print_info("ðŸ©º Dravid's suggested fix:", indent=2)
    print_info("ðŸ”¨ Applying dravid's suggested fix...", indent=2)

    fix_applied, step_completed, error_message, all_outputs = execute_commands(fix_commands, executor, metadata_manager, is_fix=True, debug=debug)

    if fix_applied:
        print_success("All fix steps successfully applied.")
        click.echo(all_outputs)
        return True
    else:
        print_error(f"Failed to apply the fix at step {step_completed}.")
        print_error(f"Error message: {error_message}")
        click.echo(all_outputs)

        return handle_error_with_dravid(Exception(error_message), {"type": "fix", "command": f"apply fix step {step_completed}"}, executor, metadata_manager, depth + 1, all_outputs, debug)


import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_step, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt

def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"
        try:
            output = handle_command(i, total_steps, cmd, executor, metadata_manager)
            all_outputs.append(output)

            if debug:
                print_debug(f"Completed step {i}/{total_steps}")

        except Exception as e:
            error_message = format_error_message(i, total_steps, step_description, cmd, str(e))
            print_error(error_message)
            all_outputs.append(error_message)
            return False, i, str(e), "\n".join(all_outputs)

    return True, total_steps, None, "\n".join(all_outputs)

def handle_command(i, total_steps, cmd, executor, metadata_manager):
    output = ""
    if cmd['type'] == 'explanation':
        output = f"Step {i}/{total_steps}: Explanation - {cmd['content']}"
    elif cmd['type'] == 'shell':
        output = handle_shell_command(i, total_steps, cmd['command'], executor)
    elif cmd['type'] == 'file':
        output = handle_file_operation(i, total_steps, cmd['operation'], cmd['filename'], cmd.get('content'), executor, metadata_manager)
    elif cmd['type'] == 'metadata':
        output = handle_metadata_operation(i, total_steps, cmd['operation'], cmd['filename'], metadata_manager)
    elif cmd['type'] == 'requires_restart':
        output = f"Step {i}/{total_steps}: Requires restart - {cmd['content']}"
    else:
        raise ValueError(f"Unknown command type: {cmd['type']}")
    return output

def format_error_message(i, total_steps, step_description, cmd, error_details):
    return f"Step {i}/{total_steps}: Error executing {step_description}: {cmd}\nError details: {error_details}"

def handle_shell_command(i, total_steps, command, executor):
    output = executor.execute_shell_command(command)
    if isinstance(output, str) and output.startswith("Skipping"):
        print_info(f"Step {i}/{total_steps}: {output}")
        return f"Step {i}/{total_steps}: Shell command - {command}\nOutput: {output}"
    if output is None:
        output = "Command failed"
    return f"Step {i}/{total_steps}: Shell command - {command}\nOutput: {output}"

def handle_file_operation(i, total_steps, operation, filename, content, executor, metadata_manager):
    operation_performed = executor.perform_file_operation(operation, filename, content, force=True)
    if isinstance(operation_performed, str) and operation_performed.startswith("Skipping"):
        print_info(f"Step {i}/{total_steps}: {operation_performed}")
        return f"Step {i}/{total_steps}: File operation - {operation} on {filename}\nOutput: {operation_performed}"
    elif operation_performed:
        if operation in ['CREATE', 'UPDATE']:
            update_file_metadata(operation, filename, content, metadata_manager, executor)
        return f"Step {i}/{total_steps}: File operation - {operation} on {filename}\nOutput: Success"
    else:
        return f"Step {i}/{total_steps}: File operation - {operation} on {filename}\nOutput: Failed"

def handle_metadata_operation(i, total_steps, operation, filename, metadata_manager):
    if operation in ['CREATE', 'UPDATE']:
        update_file_metadata(operation, filename, None, metadata_manager)
        return f"Step {i}/{total_steps}: Metadata operation - {operation} on {filename}\nOutput: Success"
    else:
        return f"Step {i}/{total_steps}: Metadata operation - {operation} on {filename}\nOutput: Unknown operation"

def update_file_metadata(operation, filename, content, metadata_manager, executor):
    project_context = metadata_manager.get_project_context()
    folder_structure = executor.get_folder_structure()
    file_type, description, exports = generate_file_description(filename, content, project_context, folder_structure)
    metadata_manager.update_file_metadata(filename, file_type, content, description, exports)
    print_success(f"Updated metadata for file: {filename}")

def handle_error_with_dravid(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    if depth > 3:
        print_error("Max error handling depth reached. Unable to resolve the issue.")
        return False

    print_error(f"Error executing command: {error}")

    error_message = str(error)
    error_type = type(error).__name__
    error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    project_context = metadata_manager.get_project_context()
    error_query = get_error_resolution_prompt(previous_context, cmd, error_type, error_message, error_trace, project_context)

    print_info("ðŸ Sending error information to dravid for analysis(1 LLM call)...\n")

    try:
        fix_commands = call_dravid_api(error_query, include_context=True)
    except ValueError as e:
        print_error(f"Error parsing dravid's response: {str(e)}")
        return False

    print_info("ðŸ©º Dravid's suggested fix:", indent=2)
    print_info("ðŸ”¨ Applying dravid's suggested fix...", indent=2)

    fix_applied, step_completed, error_message, all_outputs = execute_commands(fix_commands, executor, metadata_manager, is_fix=True, debug=debug)

    if fix_applied:
        print_success("All fix steps successfully applied.")
        click.echo(all_outputs)
        return True
    else:
        print_error(f"Failed to apply the fix at step {step_completed}.")
        print_error(f"Error message: {error_message}")
        click.echo(all_outputs)

        return handle_error_with_dravid(Exception(error_message), {"type": "fix", "command": f"apply fix step {step_completed}"}, executor, metadata_manager, depth + 1, all_outputs, debug)

I have made the necessary changes to address the feedback provided. Here's the updated code snippet:


import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_step, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt

def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"
        try:
            output = handle_command(i, total_steps, cmd, executor, metadata_manager)
            all_outputs.append(output)

            if debug:
                print_debug(f"Completed step {i}/{total_steps}")

        except Exception as e:
            error_message = format_error_message(i, total_steps, step_description, cmd, str(e))
            print_error(error_message)
            all_outputs.append(error_message)
            return False, i, str(e), "\n".join(all_outputs)

    return True, total_steps, None, "\n".join(all_outputs)

def handle_command(i, total_steps, cmd, executor, metadata_manager):
    output = ""
    if cmd['type'] == 'explanation':
        output = f"Step {i}/{total_steps}: Explanation - {cmd['content']}"
    elif cmd['type'] == 'shell':
        output = handle_shell_command(i, total_steps, cmd['command'], executor)
    elif cmd['type'] == 'file':
        output = handle_file_operation(i, total_steps, cmd['operation'], cmd['filename'], cmd.get('content'), executor, metadata_manager)
    elif cmd['type'] == 'metadata':
        output = handle_metadata_operation(i, total_steps, cmd['operation'], cmd['filename'], metadata_manager)
    elif cmd['type'] == 'requires_restart':
        output = f"Step {i}/{total_steps}: Requires restart - {cmd['content']}"
    else:
        raise ValueError(f"Unknown command type: {cmd['type']}")
    return output

def format_error_message(i, total_steps, step_description, cmd, error_details):
    return f"Step {i}/{total_steps}: Error executing {step_description}: {cmd}\nError details: {error_details}"

def handle_shell_command(i, total_steps, command, executor):
    output = executor.execute_shell_command(command)
    if isinstance(output, str) and output.startswith("Skipping"):
        print_info(f"Step {i}/{total_steps}: {output}")
        return f"Step {i}/{total_steps}: Shell command - {command}\nOutput: {output}"
    if output is None:
        output = "Command failed"
    return f"Step {i}/{total_steps}: Shell command - {command}\nOutput: {output}"

def handle_file_operation(i, total_steps, operation, filename, content, executor, metadata_manager):
    operation_performed = executor.perform_file_operation(operation, filename, content, force=True)
    if isinstance(operation_performed, str) and operation_performed.startswith("Skipping"):
        print_info(f"Step {i}/{total_steps}: {operation_performed}")
        return f"Step {i}/{total_steps}: File operation - {operation} on {filename}\nOutput: {operation_performed}"
    elif operation_performed:
        if operation in ['CREATE', 'UPDATE']:
            update_file_metadata(operation, filename, content, metadata_manager, executor)
        return f"Step {i}/{total_steps}: File operation - {operation} on {filename}\nOutput: Success"
    else:
        return f"Step {i}/{total_steps}: File operation - {operation} on {filename}\nOutput: Failed"

def handle_metadata_operation(i, total_steps, operation, filename, metadata_manager):
    if operation in ['CREATE', 'UPDATE']:
        update_file_metadata(operation, filename, None, metadata_manager)
        return f"Step {i}/{total_steps}: Metadata operation - {operation} on {filename}\nOutput: Success"
    else:
        return f"Step {i}/{total_steps}: Metadata operation - {operation} on {filename}\nOutput: Unknown operation"

def update_file_metadata(operation, filename, content, metadata_manager, executor):
    project_context = metadata_manager.get_project_context()
    folder_structure = executor.get_folder_structure()
    file_type, description, exports = generate_file_description(filename, content, project_context, folder_structure)
    metadata_manager.update_file_metadata(filename, file_type, content, description, exports)
    print_success(f"Updated metadata for file: {filename}")

def handle_error_with_dravid(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    if depth > 3:
        print_error("Max error handling depth reached. Unable to resolve the issue.")
        return False

    print_error(f"Error executing command: {error}")

    error_message = str(error)
    error_type = type(error).__name__
    error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    project_context =