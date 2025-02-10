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
    print_info("ð Starting Dravid AI...")
    if warn:
        print_warning("â ï¸ Ensure you are in a fresh directory.")
        print_warning("â ï¸ If it's an existing project, make sure you're in a git branch.")

    executor = Executor()
    metadata_manager = ProjectMetadataManager(executor.current_dir)

    try:
        project_context = metadata_manager.get_project_context()

        if project_context:
            print_info("ð Identifying relevant files for the query...")
            print_info("ð¡ LLM calls to be made: (1)", indent=2)
            files_to_modify = run_with_loader(
                lambda: get_files_to_modify(query, project_context),
                "Analyzing project files"
            )

            print_info(f"ð Found {len(files_to_modify)} potentially relevant files.")
            if debug:
                print_info("ð Possible files to be modified:")
                for file in files_to_modify:
                    print(f"  - {file}")

            print_info("ð Reading file contents...")
            file_contents = {}
            for file in files_to_modify:
                content = get_file_content(file)
                if content:
                    file_contents[file] = content
                    print_info(f"  - Read content of {file}")

            project_guidelines = fetch_project_guidelines(executor.current_dir)
            file_context = "\n".join(
                [f"Current content of {file}:\n{content}" for file, content in file_contents.items()])
            full_query = f"{project_context}\n\nProject Guidelines:\n{project_guidelines}\n\nCurrent file contents:\n{file_context}\n\nCurrent directory is not empty.\n\nUser query: {query}"
        else:
            is_empty = is_directory_empty(executor.current_dir)
            print_info("ð No project context found. Creating a new project in the current directory.")
            full_query = f"User query: {query}"

        print_info("ð¤ Preparing to send query to LLM...")
        if image_path:
            print_info(f"ð· Processing image: {image_path}", indent=4)
            print_info("ð¡ LLM calls to be made: (1)", indent=4)
            commands = run_with_loader(
                lambda: call_dravid_vision_api(
                    full_query, image_path, include_context=True, instruction_prompt=instruction_prompt),
                "Analyzing image and generating response"
            )
        else:
            print_info("ð¡ Streaming response from LLM...")
            print_info("ð¡ LLM calls to be made: (1)", indent=4)
            xml_result = stream_dravid_api(
                full_query, include_context=True, instruction_prompt=instruction_prompt, print_chunk=False)
            commands = parse_dravid_response(xml_result)
            if debug:
                print_debug(f"Received {len(commands)} new command(s)", indent=4)

        if not commands:
            print_error("ð« Failed to parse Claude's response or no commands to execute.")
            print("Actual result:", xml_result)
            return

        print_info(f"ð Parsed {len(commands)} commands from Claude's response.")

        success, step_completed, error_message, all_outputs = execute_commands(
            commands, executor, metadata_manager, debug=debug)

        if not success:
            print_error(f"ð« Failed to execute command at step {step_completed}.")
            print_error(f"Error message: {error_message}")
            print_info("ð§ Attempting to fix the error...")
            if handle_error_with_dravid(Exception(error_message), commands[step_completed-1], executor, metadata_manager, debug=debug):
                print_info("ð§ Fix applied successfully. Continuing with the remaining commands.")
                remaining_commands = commands[step_completed:]
                success, _, error_message, additional_outputs = execute_commands(
                    remaining_commands, executor, metadata_manager, debug=debug)
                all_outputs += "\n" + additional_outputs
            else:
                print_error("ð« Unable to fix the error. Skipping this command and continuing with the next.")

        print_info("ð Execution details:")
        click.echo(all_outputs)

        print_success("ð Dravid AI execution completed.")
    except Exception as e:
        print_error(f"ð« An unexpected error occurred: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()