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

If this file appears to be a dependency management file (like package.json, requirements.txt, Cargo.toml, etc.),
provide a list of external dependencies.

If it's a code file, provide a summary, list of exports (functions, classes, or variables available for importing),
and a list of imports from other project files.

Respond with an XML structure containing the metadata:

<response>
  <metadata>
    <type>file_type</type>
    <description>Detailed description based on the file's contents, project context, and folder structure</description>
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
Ensure that all other tags (type, description, file_category, exports, imports) are always present and non-empty.
If there are no exports or imports, use 'None' instead of an empty tag.
If there are no external dependencies, omit the <external_dependencies> tag entirely.
Include an <errors> tag to report any errors or warnings during the metadata generation.
"""