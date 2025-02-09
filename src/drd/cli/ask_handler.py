import click\nimport sys\nfrom ..api import stream_dravid_api, call_dravid_api_with_pagination\nfrom ..utils.utils import print_error, print_info\nfrom ..metadata.project_metadata import ProjectMetadataManager\nimport os\n\n\ndef read_file_content(file_path):\n    try:\n        with open(file_path, 'r') as file:\n            return file.read()\n    except FileNotFoundError:\n        return None\n\n\ndef suggest_file_alternative(file_path, project_metadata):\n    query = f"The file '{file_path}' doesn't exist. Can you suggest similar existing files or interpret what the user might have meant? Use the following project metadata as context:\n\n{project_metadata}"\n    response = call_dravid_api_with_pagination(query)\n    return response\n\n\ndef handle_ask_command(ask, file, debug):\n    context = ""\n    metadata_manager = ProjectMetadataManager(os.getcwd())\n    project_metadata = metadata_manager.get_project_context()\n\n    for file_path in file:\n        content = read_file_content(file_path)\n        if content is not None:\n            context += f"Content of {file_path}:\n{content}\n\n"\n        else:\n            print_error(f"File not found: {file_path}.")\n            print_info("Finding similar or alternative file")\n            print_info("LLM call to be made: 1")\n            suggestion = suggest_file_alternative(file_path, project_metadata)\n            print_info(f"Suggestion: {suggestion}")\n            user_input = click.prompt("Do you want to proceed without this file? (y/n)", type=str)\n            if user_input.lower() != 'y':\n                return\n\n    if ask:\n        context += f"User question: {ask}"\n    elif not sys.stdin.isatty():\n        context += f"User question: {sys.stdin.read().strip()}"\n    else:\n        print_error("Please provide a question using --ask or through stdin")\n        return\n\n    stream_dravid_api(context, print_chunk=True)\n