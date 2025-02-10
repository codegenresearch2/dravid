import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt

# Define constants for logging messages
STEP_START = "ðŸ”„ Step {current_step}/{total_steps}: Processing {cmd_type} {step_description}..."
SHELL_CMD_EXEC = "ðŸ’» Executing shell command: {command}"
FILE_OP_EXEC = "ðŸ“ Performing file operation: {operation} on {filename}"
METADATA_OP_EXEC = "ðŸ“‚ Updating metadata for file: {filename}"
EXPLANATION = "ðŸ’¡ Explanation: {content}"
ERROR_EXEC = "ðŸš« Error executing {step_description}: {cmd}\nError details: {error_details}"
ERROR_MAX_DEPTH = "ðŸš« Max error handling depth reached. Unable to resolve the issue."
ERROR_PARSE = "ðŸš« Error parsing dravid's response: {error_details}"
FIX_APPLY = "ðŸ”§ Applying dravid's suggested fix..."
FIX_SUCCESS = "All fix steps successfully applied."
FIX_FAIL = "ðŸš« Failed to apply the fix at step {step_completed}.\nError message: {error_message}"

def print_step(current_step, total_steps, cmd_type, step_description):
    click.echo(STEP_START.format(current_step=current_step, total_steps=total_steps, cmd_type=cmd_type, step_description=step_description))

def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"
        all_outputs.append(STEP_START.format(current_step=i, total_steps=total_steps, cmd_type=cmd['type'], step_description=step_description))

        if cmd['type'] == 'explanation':
            all_outputs.append(EXPLANATION.format(content=cmd['content']))
        else:
            try:
                if cmd['type'] == 'shell':
                    output = handle_shell_command(cmd, executor)
                elif cmd['type'] == 'file':
                    output = handle_file_operation(cmd, executor, metadata_manager)
                elif cmd['type'] == 'metadata':
                    output = handle_metadata_operation(cmd, metadata_manager)

                all_outputs.append(f"{cmd['type'].capitalize()} command - {cmd.get('command', '')} {cmd.get('operation', '')}\nOutput: {output}")

            except Exception as e:
                error_message = ERROR_EXEC.format(step_description=step_description, cmd=cmd, error_details=str(e))
                all_outputs.append(error_message)
                return False, i, str(e), "\n".join(all_outputs)

        if debug:
            all_outputs.append(f"Completed step {i}/{total_steps}")

    return True, total_steps, None, "\n".join(all_outputs)

def handle_shell_command(cmd, executor):
    print_info(SHELL_CMD_EXEC.format(command=cmd['command']))
    output = executor.execute_shell_command(cmd['command'])
    if isinstance(output, str) and output.startswith("Skipping"):
        return output
    if output is None:
        raise Exception(f"Command failed: {cmd['command']}")
    print_success(f"Successfully executed: {cmd['command']}")
    return output

def handle_file_operation(cmd, executor, metadata_manager):
    print_info(FILE_OP_EXEC.format(operation=cmd['operation'], filename=cmd['filename']))
    operation_performed = executor.perform_file_operation(cmd['operation'], cmd['filename'], cmd.get('content'), force=True)
    if isinstance(operation_performed, str) and operation_performed.startswith("Skipping"):
        return operation_performed
    elif operation_performed:
        print_success(f"Successfully performed {cmd['operation']} on file: {cmd['filename']}")
        if cmd['operation'] in ['CREATE', 'UPDATE']:
            update_file_metadata(cmd, metadata_manager, executor)
        return "Success"
    else:
        raise Exception(f"File operation failed: {cmd['operation']} on {cmd['filename']}")

def handle_metadata_operation(cmd, metadata_manager):
    if cmd['operation'] == 'UPDATE_FILE':
        if metadata_manager.update_metadata_from_file():
            print_success(METADATA_OP_EXEC.format(filename=cmd['filename']))
            return f"Updated metadata for {cmd['filename']}"
        else:
            raise Exception(f"Failed to update metadata for file: {cmd['filename']}")
    else:
        raise Exception(f"Unknown operation: {cmd['operation']}")

def update_file_metadata(cmd, metadata_manager, executor):
    project_context = metadata_manager.get_project_context()
    folder_structure = executor.get_folder_structure()
    file_type, description, exports = generate_file_description(cmd['filename'], cmd.get('content', ''), project_context, folder_structure)
    metadata_manager.update_file_metadata(cmd['filename'], file_type, cmd.get('content', ''), description, exports)

def handle_error_with_dravid(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    if depth > 3:
        return False, ERROR_MAX_DEPTH

    error_message = str(error)
    error_type = type(error).__name__
    error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    project_context = metadata_manager.get_project_context()
    error_query = get_error_resolution_prompt(previous_context, cmd, error_type, error_message, error_trace, project_context)

    print_info("ðŸ” Sending error information to dravid for analysis...")
    print_info("LLM calls to be made: 1")

    try:
        fix_commands = call_dravid_api(error_query, include_context=True)
    except ValueError as e:
        return False, ERROR_PARSE.format(error_details=str(e))

    print_info("ðŸ’¡ dravid's suggested fix:")
    print_info(FIX_APPLY)

    fix_applied, step_completed, error_message, all_outputs = execute_commands(fix_commands, executor, metadata_manager, is_fix=True, debug=debug)

    if fix_applied:
        print_success(FIX_SUCCESS)
        print_info("Fix application details:")
        click.echo(all_outputs)
        return True, None
    else:
        return False, FIX_FAIL.format(step_completed=step_completed, error_message=error_message)