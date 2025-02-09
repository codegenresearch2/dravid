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
    else:
        file_type = "code_file"

    # Determine exports and imports based on the file content
    if file_type == "code_file":
        for line in content.splitlines():
            if line.startswith("def "):
                exports_info.append(f"fun:{line.split('def ')[1].split('(')[0]}")
            elif line.startswith("class "):
                exports_info.append(f"class:{line.split('class ')[1].split('(')[0]}")
            elif ":" in line and "import" in line:
                imports_info.append(line.split("import ")[1].split(" ")[0])

    # Determine external dependencies based on the file content
    if file_type == "dependency_file":
        for line in content.splitlines():
            if "==" in line:
                external_dependencies.append(line.split("==")[0])

    # Construct the XML response
    response = f"""
<response>
  <metadata>
    <type>{file_type}</type>
    <summary>Description based on the file's contents, project context, and folder structure</summary>
    <file_category>{file_type}</file_category>
    <exports>{','.join(exports_info) if exports_info else 'None'}</exports>
    <imports>{','.join(imports_info) if imports_info else 'None'}</imports>
    <external_dependencies>
      {' '.join([f"<dependency>{dep}</dependency>" for dep in external_dependencies]) if external_dependencies else ''}
    </external_dependencies>
  </metadata>
</response>
"""
    return response