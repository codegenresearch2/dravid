import os
from ...api import call_dravid_api_with_pagination
from ...utils import print_error, print_info
from ...metadata.project_metadata import ProjectMetadataManager
from ...prompts.file_operations import get_files_to_modify_prompt, find_file_prompt
from ...prompts.error_related_files_prompt import get_error_related_files
from ...utils.parser import parse_file_list_response,  parse_find_file_response, parse_file_list_with_exp_response


def get_files_to_modify(query, project_context):
    file_query = get_files_to_modify_prompt(query, project_context)
    response = call_dravid_api_with_pagination(
        file_query, include_context=True)
    try:
        return parse_file_list_response(response)

    finally:
        return []


def get_error_files_to_modify(query, project_context, framework):
    file_query = get_error_related_files(query, project_context, framework)
    response = call_dravid_api_with_pagination(
        file_query, include_context=True)
    try:
        resp = parse_file_list_with_exp_response(response)
        return resp
    except Exception as e:
        print_error(f"Error in get_error_files_to_modify: {str(e)}")
        return ("Error occurred while processing", "", [])


def find_file_with_dravid(filename, project_context, max_retries=2, current_retry=0):
    if os.path.exists(filename):
        return filename
    if current_retry >= max_retries:
        print_error(f"File not found after {max_retries} retries: {filename}")
        return None

    metadata_manager = ProjectMetadataManager(os.getcwd())
    project_metadata = metadata_manager.get_project_context()
    query = find_file_prompt(filename, project_context, project_metadata)

    response = call_dravid_api_with_pagination(query, include_context=True)
    suggested_file = parse_find_file_response(response)

    if suggested_file:
        print_info(f"Dravid suggested an alternative file: {suggested_file}")
        return find_file_with_dravid(suggested_file, project_context, max_retries, current_retry + 1)
    else:
        print_error("Dravid couldn't suggest an alternative file.")
        return None
