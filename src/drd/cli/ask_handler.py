import click
import sys
from ..utils.api_utils import stream_claude_response, call_dravid_api
from ..utils.utils import print_error, print_info
from ..metadata.project_metadata import ProjectMetadataManager
import os


def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None


def suggest_file_alternative(file_path, project_metadata):
    query = f"The file '{file_path}' doesn't exist. Can you suggest similar existing files or interpret what the user might have meant? Use the following project metadata as context:\n\n{project_metadata}"
    response = call_dravid_api(query)
    return response


def handle_ask_command(ask, file, debug):
    context = ""
    metadata_manager = ProjectMetadataManager(os.getcwd())
    project_metadata = metadata_manager.get_project_context()

    for file_path in file:
        content = read_file_content(file_path)
        if content is not None:
            context += f"Content of {file_path}:\n{content}\n\n"
        else:
            print_error(f"File not found: {file_path}")
            suggestion = suggest_file_alternative(file_path, project_metadata)
            print_info(f"Suggestion: {suggestion}")
            user_input = click.prompt(
                "Do you want to proceed without this file? (y/n)", type=str)
            if user_input.lower() != 'y':
                return

    if ask:
        context += f"User question: {ask}\n"
    elif not sys.stdin.isatty():
        context += f"User question: {sys.stdin.read().strip()}\n"
    else:
        print_error("Please provide a question using --ask or through stdin")
        return

    stream_claude_response(context, debug)
