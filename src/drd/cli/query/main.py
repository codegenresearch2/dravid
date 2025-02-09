import click\\\nfrom ...api.main import stream_dravid_api, call_dravid_vision_api\\\\nfrom ...utils.step_executor import Executor\\\\nfrom ...metadata.project_metadata import ProjectMetadataManager\\\\nfrom .dynamic_command_handler import handle_error_with_dravid, execute_commands\\\\nfrom ...utils import print_error, print_success, print_info, print_step, print_debug, print_warning, run_with_loader\\\\nfrom ...utils.file_utils import get_file_content, fetch_project_guidelines\\\\nfrom ...metadata.common_utils import generate_file_description\\\\nfrom .file_operations import get_files_to_modify\\\\nfrom ...utils.parser import parse_dravid_response\\\\n\\n\\ndef execute_dravid_command(query, image_path, debug, instruction_prompt=None):\\\\\n    print_info("Starting Dravid CLI tool..")\\\\\n    print_warning("Please make sure you are in a fresh directory.")\\\\\n    print_warning("If it is an existing project, please ensure you're in a git branch")\\\\\n    print_warning("Use Ctrl+C to exit if you're not")\\\\\n\\\\n    executor = Executor()\\\\\n    metadata_manager = ProjectMetadataManager(executor.current_dir)\\\\\n\\\\n    try:\\\\\n        project_context = metadata_manager.get_project_context()\\\\\n\\\\n        if project_context:\\\\\n            print_info("Identifying related files to the query...")\\\\\n            print_info("LLM calls to be made: 1")\\\\\n            files_to_modify = run_with_loader(\\\\n                lambda: get_files_to_modify(query, project_context),\\\\\n                "Analyzing project files"\\\\\n            )\\\\\n\\\\n            print_info(f"Found {len(files_to_modify)} potentially relevant files.")\\\\\n            file_contents = {}\\\\\n            for file in files_to_modify:\\\\\n                content = get_file_content(file)\\\\\n                if content:\\\\\n                    file_contents[file] = content\\\\\n                    print_info(f"  - Read content of {file}")\\\\\n\\\\n            project_guidelines = fetch_project_guidelines(executor.current_dir)\\\\\n            file_context = "\n".join([f"Current content of {file}:\n{content}" for file, content in file_contents.items()]) \\\\\n            full_query = (f"{project_context}\n\nProject Guidelines:\n{project_guidelines}\n\nCurrent file contents:\n{file_context}\n\nUser query: {query}")\\\\\n        else:\\\\\n            print_info("No current project context found. Will create a new project in the current directory.")\\\\\n            full_query = f"User query: {query}"\\\\\n\\\\n        print_info("Preparing to send query to Claude API...") \\\\\n        if image_path:\\\\\n            print_info(f"Processing image: {image_path}") \\\\\n            print_info("LLM calls to be made: 1") \\\\\n            commands = run_with_loader(\\\\n                lambda: call_dravid_vision_api(full_query, image_path, include_context=True, instruction_prompt=instruction_prompt),\\\\\n                "Analyzing image and generating response"\\\\\n            )\\\\\n        else:\\\\\n            print_info("Streaming response from Claude API...") \\\\\n            print_info("LLM calls to be made: 1") \\\\\n            xml_result = stream_dravid_api(full_query, include_context=True, instruction_prompt=instruction_prompt, print_chunk=False)\\\\\n            commands = parse_dravid_response(xml_result)\\\\\n\\\\n            if not commands:\\\\\n                print_error("Failed to parse Claude's response or no commands to execute.")\\\\\n                return\\\\\n\\\\n            print_info(f"Parsed {len(commands)} commands from Claude's response.") \\\\\n\\\\n            success, step_completed, error_message, all_outputs = execute_commands(commands, executor, metadata_manager, debug=debug)\\\\\n\\\\n            if not success:\\\\\n                print_error(f"Failed to execute command at step {step_completed}.")\\\\\n                print_error(f"Error message: {error_message}")\\\\\n                print_info("Attempting to fix the error...") \\\\\n                if handle_error_with_dravid(Exception(error_message), commands[step_completed-1], executor, metadata_manager, debug=debug):\\\\\n                    print_info("Fix applied successfully. Continuing with the remaining commands.") \\\\\n                    remaining_commands = commands[step_completed:] \\\\\n                    success, _, error_message, additional_outputs = execute_commands(remaining_commands, executor, metadata_manager, debug=debug)\\\\\n                    all_outputs += "\n" + additional_outputs \\\\\n                else:\\\\\n                    print_error("Unable to fix the error. Skipping this command and continuing with the next.") \\\\\n\\\\n            print_info("Execution details:") \\\\\n            click.echo(all_outputs) \\\\\n\\\\n            print_success("Dravid CLI tool execution completed.") \\\\\n    except Exception as e:\\\\\n        print_error(f"An unexpected error occurred: {str(e)}") \\\\\n        if debug:\\\\\n            import traceback \\\\\n            traceback.print_exc() \\\\\n