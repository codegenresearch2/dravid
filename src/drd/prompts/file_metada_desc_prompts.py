def get_file_metadata_prompt(filename, content, project_context, folder_structure):
    return f"""
{project_context}
Current folder structure:
{folder_structure}
File: {filename}
Content:
{content}

You're the project context maintainer. Your role is to keep relevant meta info about the entire project
so it can be used by an AI coding assistant in future for reference.

Based on the file content, project context, and the current folder structure,
please generate appropriate metadata for this file.

Respond with an XML structure containing the metadata:

<response>
  <metadata>
    <path>{filename}</path>
    <type>file_type</type>
    <summary>Brief summary of the file's main purpose</summary>
    <file_category>code_file or dependency_file</file_category>
    <exports>fun:functionName,class:ClassName,var:variableName or None</exports>
    <imports>path/to/file:importedName or None</imports>
    <external_dependencies>
      <dependency>
        <name>name1</name>
        <version>version1</version>
      </dependency>
      <!-- Add more dependency elements as needed -->
    </external_dependencies>
  </metadata>
  <errors>
    <!-- If there are any errors or warnings during the metadata generation, include them here -->
    <error>Error message</error>
  </errors>
</response>

Respond strictly only with the XML response as it will be used for parsing.
Ensure that all other tags (path, type, summary, file_category, exports, imports) are always present and non-empty.
If there are no exports or imports, use 'None' instead of an empty tag.
If there are no external dependencies, omit the <external_dependencies> tag entirely.
Include an <errors> tag to report any errors or warnings during the metadata generation.
"""