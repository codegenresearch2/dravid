import asyncio
from ..api.main import call_dravid_api_with_pagination
from ..utils.parser import extract_and_parse_xml
from .project_metadata import ProjectMetadataManager
from ..utils import print_error, print_success, print_info, print_warning
from .common_utils import get_ignore_patterns, get_folder_structure, find_file_with_dravid
from ..prompts.metadata_update_prompts import get_files_to_update_prompt

async def update_metadata_with_dravid_async(meta_description, current_dir):
    print_info("Updating metadata based on the provided description...")
    metadata_manager = ProjectMetadataManager(current_dir)
    project_context = metadata_manager.get_project_context()

    ignore_patterns, ignore_message = get_ignore_patterns(current_dir)
    print_info(ignore_message)

    folder_structure = get_folder_structure(current_dir, ignore_patterns)
    print_info("Current folder structure:")
    print_info(str(folder_structure))

    files_query = get_files_to_update_prompt(
        project_context, folder_structure, meta_description)
    files_response = call_dravid_api_with_pagination(
        files_query, include_context=True)

    try:
        root = extract_and_parse_xml(files_response)
        files_to_process = root.findall('.//file')

        if not files_to_process:
            print_info("No files identified for metadata update or removal.")
            return

        print_info(
            f"Files identified for processing: {', '.join([file.find('path').text.strip() for file in files_to_process if file.find('path') is not None])}")

        for file in files_to_process:
            path = file.find('path').text.strip() if file.find(
                'path') is not None else ""
            action = file.find('action').text.strip() if file.find(
                'action') is not None else "update"

            if not path:
                print_warning("Skipping file with empty path")
                continue

            if action == 'remove':
                metadata_manager.remove_file_metadata(path)
                print_success(f"Removed metadata for file: {path}")
                continue

            found_filename = find_file_with_dravid(
                path, project_context, folder_structure)
            if not found_filename:
                print_warning(f"Could not find file: {path}")
                continue

            try:
                # Analyze the file
                file_info = await metadata_manager.analyze_file(found_filename)

                if file_info:
                    # Update the metadata
                    metadata_manager.update_file_metadata(
                        file_info['path'],
                        file_info['type'],
                        file_info['summary'],
                        file_info['exports'],
                        file_info['imports']
                    )
                    print_success(
                        f"Updated metadata for file: {found_filename}")

                    # Add external dependencies
                    dependencies = file.find('metadata').find('external_dependencies')
                    if dependencies is not None:
                        for dep in dependencies.findall('dependency'):
                            metadata_manager.add_external_dependency(dep.text)
                else:
                    print_warning(f"Could not analyze file: {found_filename}")

            except Exception as e:
                print_error(f"Error processing {found_filename}: {str(e)}")

        # After processing all files, update the environment info
        metadata_manager.update_environment_info_from_key_files()

        print_success("Metadata update completed.")
    except Exception as e:
        print_error(f"Error parsing dravid's response: {str(e)}")
        print_error(f"Raw response: {files_response}")

def update_metadata_with_dravid(meta_description, current_dir):
    asyncio.run(update_metadata_with_dravid_async(
        meta_description, current_dir))


In the updated code, the project metadata manager is used to handle the updating and removal of file metadata. External dependencies are added during the file processing loop. After processing all files, the environment info is updated using the `update_environment_info_from_key_files` method.

The code now provides more clear metadata structure in responses, improved error handling and reporting, and the enhancement of test coverage is addressed by the existing test cases provided in `test_updater.py`. This test suite ensures that the metadata updater function behaves as expected, including checking if metadata is correctly updated and removed, if external dependencies are added, and if appropriate messages are printed.