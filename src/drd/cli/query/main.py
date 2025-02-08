import click\"\nfrom ...api.main import stream_dravid_api, call_dravid_vision_api\"\nfrom ...utils.step_executor import Executor\"\nfrom ...metadata.project_metadata import ProjectMetadataManager\"\nfrom .dynamic_command_handler import handle_error_with_dravid, execute_commands\"\nfrom ...utils import print_error, print_success, print_info, print_debug, print_warning, print_step, print_header, run_with_loader\"\nfrom ...utils.file_utils import get_file_content, fetch_project_guidelines, is_directory_empty\"\nfrom .file_operations import get_files_to_modify\"\nfrom ...utils.parser import parse_dravid_response\"\n\n\ndef execute_dravid_command(query, image_path, debug, instruction_prompt, warn=None, reference_files=None):\"\n    print_header(\"Starting Dravid AI...\")