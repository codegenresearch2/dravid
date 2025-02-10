import click
from ...api.main import stream_dravid_api, call_dravid_vision_api
from ...utils.step_executor import Executor
from ...metadata.project_metadata import ProjectMetadataManager
from .dynamic_command_handler import handle_error_with_dravid, execute_commands
from ...utils import print_error, print_success, print_info, print_debug, print_warning, run_with_loader
from ...utils.file_utils import get_file_content, fetch_project_guidelines
from .file_operations import get_files_to_modify
from ...utils.parser import parse_dravid_response

def execute_dravid_command(query, image_path=None, debug=False, instruction_prompt=None):
    print_info("Starting Dravid CLI tool..")
    print_warning("Ensure you're in a fresh directory and a git branch if it's an existing project.")
    print_warning("Press Ctrl+C to exit if not.")

    executor = Executor()
    metadata_manager = ProjectMetadataManager(executor.current_dir)

    try:
        project_context = metadata_manager.get_project_context()
        full_query = prepare_query(query, project_context, image_path, executor)

        print_info("Preparing to send query to Claude API...")
        print_info("LLM calls to be made: 1")
        commands = get_commands(full_query, image_path, instruction_prompt)

        if debug:
            print_debug(f"Received {len(commands)} new command(s)")

        if not commands:
            print_error("Failed to parse Claude's response or no commands to execute.")
            return

        execute_and_handle_commands(commands, executor, metadata_manager, debug)

        print_success("Dravid CLI tool execution completed.")
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()

def prepare_query(query, project_context, image_path, executor):
    if project_context:
        print_info("Identifying related files to the query...")
        files_to_modify = run_with_loader(lambda: get_files_to_modify(query, project_context), "Analyzing project files")

        print_info(f"Found {len(files_to_modify)} potentially relevant files.")
        print_info("Reading file contents...")
        file_contents = {}
        for file in files_to_modify:
            content = get_file_content(file)
            if content:
                file_contents[file] = content
                print_info(f"  - Read content of {file}")

        project_guidelines = fetch_project_guidelines(executor.current_dir)
        file_context = "\n".join([f"Current content of {file}:\n{content}" for file, content in file_contents.items()])
        full_query = f"{project_context}\n\nProject Guidelines:\n{project_guidelines}\n\nCurrent file contents:\n{file_context}\n\nUser query: {query}"
    else:
        print_info("No current project context found. Will create a new project in the current directory.")
        full_query = f"User query: {query}"
    return full_query

def get_commands(query, image_path, instruction_prompt):
    try:
        if image_path:
            print_info(f"Processing image: {image_path}")
            commands = run_with_loader(lambda: call_dravid_vision_api(query, image_path, include_context=True, instruction_prompt=instruction_prompt), "Analyzing image and generating response")
        else:
            print_info("Streaming response from Claude API...")
            xml_result = stream_dravid_api(query, include_context=True, instruction_prompt=instruction_prompt, print_chunk=False)
            commands = parse_dravid_response(xml_result)
        return commands
    except NameError as e:
        print_error(f"An error occurred: {str(e)}")
        return None

def execute_and_handle_commands(commands, executor, metadata_manager, debug):
    success, step_completed, error_message, all_outputs = execute_commands(commands, executor, metadata_manager, debug=debug)
    if not success:
        print_error(f"Failed to execute command at step {step_completed}.")
        print_error(f"Error message: {error_message}")
        print_info("Attempting to fix the error...")
        if handle_error_with_dravid(Exception(error_message), commands[step_completed-1], executor, metadata_manager, debug=debug):
            print_info("Fix applied successfully. Continuing with the remaining commands.")
            remaining_commands = commands[step_completed:]
            success, _, error_message, additional_outputs = execute_commands(remaining_commands, executor, metadata_manager, debug=debug)
            all_outputs += "\n" + additional_outputs
        else:
            print_error("Unable to fix the error. Skipping this command and continuing with the next.")
    print_info("Execution details:")
    click.echo(all_outputs)