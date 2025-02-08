import asyncio\nfrom drd.api.main import call_dravid_api_with_pagination\nfrom drd.utils.parser import extract_and_parse_xml\nfrom drd.metadata.project_metadata import ProjectMetadataManager\nfrom drd.utils import print_error, print_success, print_info, print_warning\nfrom drd.metadata.common_utils import get_ignore_patterns, get_folder_structure, find_file_with_dravid\nfrom drd.prompts.metadata_update_prompts import get_files_to_update_prompt\n\nasync def update_metadata_with_dravid_async(meta_description, current_dir):\n    print_info("Updating metadata based on the provided description...") \n    metadata_manager = ProjectMetadataManager(current_dir) \n    project_context = metadata_manager.get_project_context() \n\n    ignore_patterns, ignore_message = get_ignore_patterns(current_dir) \n    print_info(ignore_message) \n\n    folder_structure = get_folder_structure(current_dir, ignore_patterns) \n    print_info("Current folder structure:") \n    print_info(folder_structure) \n\n    files_query = get_files_to_update_prompt(project_context, folder_structure, meta_description) \n    files_response = call_dravid_api_with_pagination(files_query, include_context=True) \n\n    try: \n        root = extract_and_parse_xml(files_response) \n        files_to_process = root.findall('.//file') \n\n        if not files_to_process: \n            print_info("No files identified for metadata update or removal.") \n            return \n\n        print_info(f"Files identified for processing: {', '.join([file.find('path').text.strip() for file in files_to_process if file.find('path') is not None])} ") \n\n        for file in files_to_process: \n            path = file.find('path').text.strip() if file.find('path') is not None else "" \n            action = file.find('action').text.strip() if file.find('action') is not None else "update" \n\n            if not path: \n                print_warning("Skipping file with empty path") \n                continue \n\n            if action == 'remove': \n                metadata_manager.remove_file_metadata(path) \n                print_success(f"Removed metadata for file: {path}") \n                continue \n\n            found_filename = find_file_with_dravid(path, project_context, folder_structure) \n            if not found_filename: \n                print_warning(f"Could not find file: {path}") \n                continue \n\n            try: \n                file_info = await metadata_manager.analyze_file(found_filename) \n\n                if file_info: \n                    metadata_manager.update_file_metadata(file_info['path'], file_info['type'], file_info['summary'], file_info['exports'], file_info['imports']) \n                    print_success(f"Updated metadata for file: {found_filename}") \n                else: \n                    print_warning(f"Could not analyze file: {found_filename}") \n\n            except Exception as e: \n                print_error(f"Error processing {found_filename}: {str(e)}") \n\n        all_languages = set(file['type'] for file in metadata_manager.metadata['key_files'] if file['type'] not in ['binary', 'unknown']) \n        if all_languages: \n            primary_language = max(all_languages, key=lambda x: sum(1 for file in metadata_manager.metadata['key_files'] if file['type'] == x)) \n            other_languages = list(all_languages - {primary_language}) \n            metadata_manager.update_environment_info(primary_language=primary_language, other_languages=other_languages, primary_framework=metadata_manager.metadata['environment']['primary_framework'], runtime_version=metadata_manager.metadata['environment']['runtime_version']) \n\n        print_success("Metadata update completed.") \n    except Exception as e: \n        print_error(f"Error parsing dravid's response: {str(e)}") \n        print_error(f"Raw response: {files_response}") \n\n\ndef update_metadata_with_dravid(meta_description, current_dir):\n    asyncio.run(update_metadata_with_dravid_async(meta_description, current_dir))