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
    <summary>A concise description of the file's main purpose and functionality</summary>
    <file_category>code_file or dependency_file</file_category>
    <exports>Comma-separated list of exports (functions, classes, or variables) or 'None'</exports>
    <imports>Comma-separated list of imports (path/to/file:importedName) or 'None'</imports>
    <external_dependencies>
      <!-- Add dependency elements as needed -->
      <dependency>
        <name>name1</name>
        <version>version1</version>
      </dependency>
    </external_dependencies>
  </metadata>
  <guidelines>
    <1>Path: Full path of the file within the project</1>
    <2>Type: Programming language or file type (e.g., "typescript", "python", "json")</2>
    <3>Summary: Concise description of the file's main purpose and functionality</3>
    <4>File Category: code_file or dependency_file</4>
    <5>Exports: Comma-separated list of exports (functions, classes, or variables) or 'None'</5>
    <6>Imports: Comma-separated list of imports (path/to/file:importedName) or 'None'</6>
    <7>External Dependencies: List of external dependencies (name and version) or omit if none</7>
  </guidelines>
  <examples>
    <code_file>
      <path>src/main.py</path>
      <type>python</type>
      <summary>Main entry point for the application</summary>
      <file_category>code_file</file_category>
      <exports>None</exports>
      <imports>utils.py:utils</imports>
    </code_file>
    <dependency_file>
      <path>requirements.txt</path>
      <type>dependency_file</type>
      <summary>List of external dependencies for the project</summary>
      <file_category>dependency_file</file_category>
      <exports>None</exports>
      <imports>None</imports>
      <external_dependencies>
        <dependency>
          <name>numpy</name>
          <version>1.21.2</version>
        </dependency>
      </external_dependencies>
    </dependency_file>
  </examples>
</response>

Respond strictly only with the XML response as it will be used for parsing.
Ensure that all other tags (path, type, summary, file_category, exports, imports) are always present and non-empty.
If there are no exports or imports, use 'None' instead of an empty tag.
If there are no external dependencies, omit the <external_dependencies> tag entirely.
Include a <guidelines> tag to clarify how each field should be populated based on the context.
Include an <examples> tag to provide examples of the expected XML output for different scenarios.
"""