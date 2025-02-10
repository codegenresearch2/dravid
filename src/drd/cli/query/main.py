import click
from ...api.main import stream_dravid_api, call_dravid_vision_api
from ...utils.step_executor import Executor
from ...metadata.project_metadata import ProjectMetadataManager
from .dynamic_command_handler import handle_error_with_dravid, execute_commands
from ...utils import print_error, print_success, print_info, print_debug, print_warning, run_with_loader
from ...utils.file_utils import get_file_content, fetch_project_guidelines, is_directory_empty
from .file_operations import get_files_to_modify
from ...utils.parser import parse_dravid_response

def execute_dravid_command(query, image_path, debug, instruction_prompt, warn=None):
    print_info("Starting Dravid CLI tool...", indent=0)
    if warn:
        print_warning("Please make sure you are in a fresh directory.")
        print_warning("If it is an existing project, please ensure you're in a git branch.")

    executor = Executor()
    metadata_manager = ProjectMetadataManager(executor.current_dir)

    try:
        project_context = metadata_manager.get_project_context()

        if project_context:
            print_info("Identifying related files to the query...", indent=1)
            print_info("LLM calls to be made: (1)", indent=2)
            files_to_modify = run_with_loader(
                lambda: get_files_to_modify(query, project_context),
                "Analyzing project files"
            )

            print_info(f"Found {len(files_to_modify)} potentially relevant files.", indent=1)
            if debug:
                print_info("Possible files to be modified:", indent=2)
                for file in files_to_modify:
                    print(f"  - {file}")

            print_info("Reading file contents...", indent=1)
            file_contents = {}
            for file in files_to_modify:
                content = get_file_content(file)
                if content:
                    file_contents[file] = content
                    print_info(f"Read content of {file}", indent=2)

            project_guidelines = fetch_project_guidelines(executor.current_dir)
            file_context = "\n".join(
                [f"Current content of {file}:\n{content}" for file, content in file_contents.items()])
            full_query = f"{project_context}\n\nProject Guidelines:\n{project_guidelines}\n\nCurrent file contents:\n{file_context}\n\nCurrent directory is not empty.\n\nUser query: {query}"
        else:
            is_empty = is_directory_empty(executor.current_dir)
            print_info("No current project context found. Will create a new project in the current directory.", indent=1)
            full_query = f"User query: {query}"

        print_info("Preparing to send query to LLM...", indent=1)
        if image_path:
            print_info(f"Processing image: {image_path}", indent=2)
            print_info("LLM calls to be made: (1)", indent=2)
            commands = run_with_loader(
                lambda: call_dravid_vision_api(
                    full_query, image_path, include_context=True, instruction_prompt=instruction_prompt),
                "Analyzing image and generating response"
            )
        else:
            print_info("Streaming response from LLM...", indent=2)
            print_info("LLM calls to be made: (1)", indent=2)
            xml_result = stream_dravid_api(
                full_query, include_context=True, instruction_prompt=instruction_prompt, print_chunk=False)
            commands = parse_dravid_response(xml_result)
            if debug:
                print_debug(f"Received {len(commands)} new command(s)", indent=2)

        if not commands:
            print_error("Failed to parse Claude's response or no commands to execute.")
            print("Actual result:", xml_result)
            return

        print_info(f"Parsed {len(commands)} commands from Claude's response.", indent=1)

        success, step_completed, error_message, all_outputs = execute_commands(
            commands, executor, metadata_manager, debug=debug)

        if not success:
            print_error(f"Failed to execute command at step {step_completed}.")
            print_error(f"Error message: {error_message}")
            print_info("Attempting to fix the error...", indent=2)
            if handle_error_with_dravid(Exception(error_message), commands[step_completed-1], executor, metadata_manager, debug=debug):
                print_info("Fix applied successfully. Continuing with the remaining commands.", indent=2)
                remaining_commands = commands[step_completed:]
                success, _, error_message, additional_outputs = execute_commands(
                    remaining_commands, executor, metadata_manager, debug=debug)
                all_outputs += "\n" + additional_outputs
            else:
                print_error("Unable to fix the error. Skipping this command and continuing with the next.")

        print_info("Execution details:", indent=1)
        click.echo(all_outputs)

        print_success("Dravid CLI tool execution completed.")
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()