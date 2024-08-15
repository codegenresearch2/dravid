import traceback
from ...api.main import call_dravid_api
from ...utils.step_executor import Executor
from ...utils.utils import print_error, print_success, print_info, print_prompt
from ...utils.loader import run_with_loader
from ...prompts.monitor_error_resolution import get_error_resolution_prompt
from ..query.file_operations import get_error_files_to_modify
from ...utils.file_utils import get_file_content
import logging


def monitoring_handle_error_with_dravid(error, error_trace, monitor):

    logger = logging.getLogger(__name__)
    logger.info(f"Starting error handling for: {error}")

    # error_message = str(error)
    # error_type = type(error).__name__
    # error_trace = ''.join(traceback.format_exception(
    #     type(error), error, error.__traceback__))
    project_context = monitor.metadata_manager.get_project_context()
    framework = monitor.metadata_manager.get_project_framework()

    print_info("Identifying relevant files for error context...")

    explanation, files_to_check = run_with_loader(
        lambda: get_error_files_to_modify(
            error_trace, project_context, framework),
        "Analyzing project files"
    )
    print_info(explanation)

    user_feedback = input(
        "\nDo you have any feedback or additional points? (Press Enter to proceed, or type your feedback): ")

    file_contents = {}
    for file in files_to_check:
        content = get_file_content(file)
        if content:
            file_contents[file] = content
            print_info(f"  - Read content of {file}")

    file_context = "\n".join(
        [f"Content of {file}:\n{content}" for file,
            content in file_contents.items()]
    )

    error_query = get_error_resolution_prompt(
        explanation, project_context, file_context, framework, user_feedback
    )

    print_info("🔍 Sending error information to Dravid for analysis...")
    try:
        commands = call_dravid_api(error_query, include_context=True)
    except ValueError as e:
        print_error(f"Error parsing dravid's response: {str(e)}")
        return False

    requires_restart = False
    fix_commands = []
    print_prompt("Dravid's suggested fix after checking files:\n")
    for command in commands:
        if command['type'] == 'requires_restart':
            requires_restart = command['content'].lower() == 'true'
        elif command['type'] == 'explanation':
            print_info(command.get('content'))
        else:
            fix_commands.append(command)

    executor = Executor()
    for cmd in fix_commands:
        if cmd['type'] == 'shell':
            executor.execute_shell_command(cmd['command'])
        elif cmd['type'] == 'file':
            executor.perform_file_operation(
                cmd['operation'], cmd['filename'], cmd.get('content'))

    print_success("Fix applied.")

    logger.info(f"User response to restart: ")
    if requires_restart:
        print_info("The applied fix requires a server restart.")
        restart_input = input(
            "Do you want to restart the server now? [y/N]: "
        )
        if restart_input.lower() == 'y':
            print_info("Requesting server restart...")
            monitor.perform_restart()
        else:
            print_info(
                "Server restart postponed. You may need to restart manually if issues persist.")
    else:
        print_info("The applied fix does not require a server restart.")

    logger.info("Error handling completed")
    return True
