def get_file_metadata_prompt(filename, content, project_context, folder_structure):
    # Initialize lists for exports, imports, and external dependencies
    exports_info = []
    imports_info = []
    external_dependencies = []

    # Determine the file type based on the content or filename
    if "requirements.txt" in filename:
        file_type = "python"
    elif "package.json" in filename:
        file_type = "javascript"
    elif "tsconfig.json" in filename:
        file_type = "typescript"
    elif "composer.json" in filename:
        file_type = "php"
    elif "Cargo.toml" in filename:
        file_type = "rust"
    else:
        file_type = "code_file"

    # Determine exports and imports based on the file content
    if file_type == "code_file":
        for line in content.splitlines():
            if line.startswith("def "):
                func_name = line.split('def ')[1].split('(')[0]
                exports_info.append(f"fun:{func_name}")
            elif line.startswith("class "):
                class_name = line.split('class ')[1].split('(')[0]
                exports_info.append(f"class:{class_name}")
            elif ":" in line and "import" in line:
                import_parts = line.split("import ")
                for part in import_parts:
                    if ":" in part:
                        import_item = part.split(" ")[0]
                        imports_info.append(f"{import_item}")

    # Determine external dependencies based on the file content
    if file_type == "dependency_file":
        for line in content.splitlines():
            if "==" in line:
                external_dependencies.append(line.split("==")[0])

    # Generate a summary based on the file's contents
    summary = "Summary based on the file's contents, project context, and folder structure"

    # Construct the XML response
    response = f"""
<response>
  <metadata>
    <path>{filename}</path>
    <type>{file_type}</type>
    <summary>{summary}</summary>
    <file_category>{file_type}</file_category>
    <exports>{','.join(exports_info) if exports_info else 'None'}</exports>
    <imports>{','.join(imports_info) if imports_info else 'None'}</imports>
    <external_dependencies>
      {' '.join([f"<dependency>{dep}</dependency>" for dep in external_dependencies]) if external_dependencies else ''}
    </external_dependencies>
    <project_context>{project_context}</project_context>
    <folder_structure>{folder_structure}</folder_structure>
  </metadata>
</response>
"""
    return response