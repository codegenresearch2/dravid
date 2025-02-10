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
    print_info("ð Starting Dravid CLI tool...")
    if warn:
        print_warning("â ï¸ Ensure you're in a fresh directory or a git branch for existing projects.")

    executor = Executor()
    metadata_manager = ProjectMetadataManager(executor.current_dir)

    try:
        project_context = metadata_manager.get_project_context()
        if project_context:
            print_info("ð Analyzing project files for relevance...")
            files_to_modify = run_with_loader(
                lambda: get_files_to_modify(query, project_context),
                "Analyzing project files"
            )
            print_info(f"ð Found {len(files_to_modify)} potentially relevant files.")
            if debug:
                print_info("ð Possible files to be modified:")
                for file in files_to_modify:
                    print(f"  - {file}")

            print_info("ð Reading file contents...")
            file_contents = {file: get_file_content(file) for file in files_to_modify if get_file_content(file)}
            for file in file_contents:
                print_info(f"  â
 Read content of {file}")

            project_guidelines = fetch_project_guidelines(executor.current_dir)
            file_context = "\n".join(
                [f"Current content of {file}:\n{content}" for file, content in file_contents.items()])
            full_query = f"{project_context}\nProject Guidelines:\n{project_guidelines}\nCurrent file contents:\n{file_context}\nUser query: {query}"
        else:
            print_info("ð Creating new project in the current directory.")
            full_query = f"User query: {query}"

        print_info("ð¤ Sending query to LLM...")
        if image_path:
            print_info(f"ð¼ï¸  Processing image: {image_path}")
            commands = run_with_loader(
                lambda: call_dravid_vision_api(full_query, image_path, include_context=True, instruction_prompt=instruction_prompt),
                "Analyzing image and generating response"
            )
        else:
            xml_result = stream_dravid_api(full_query, include_context=True, instruction_prompt=instruction_prompt, print_chunk=False)
            commands = parse_dravid_response(xml_result)
            if debug:
                print_debug(f"ð¥ Received {len(commands)} new command(s)")

        assert commands, "â Failed to parse LLM's response or no commands to execute."
        print_info(f"â
 Parsed {len(commands)} commands from LLM's response.")

        success, step_completed, error_message, all_outputs = execute_commands(commands, executor, metadata_manager, debug=debug)
        if not success:
            print_error(f"â Failed to execute command at step {step_completed}.")
            print_info("ð§ Attempting to fix the error...")
            if handle_error_with_dravid(Exception(error_message), commands[step_completed-1], executor, metadata_manager, debug=debug):
                print_info("â
 Fix applied. Continuing with the remaining commands.")
                success, _, error_message, additional_outputs = execute_commands(commands[step_completed:], executor, metadata_manager, debug=debug)
                all_outputs += "\n" + additional_outputs
            else:
                print_error("â Unable to fix error. Skipping this command.")

        print_info("ð Execution details:")
        click.echo(all_outputs)
        print_success("â
 Dravid CLI tool execution completed.")
    except Exception as e:
        print_error(f"â An unexpected error occurred: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()