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
  <guidelines>
    <instruction>1. Ensure all fields are included in the XML response.</instruction>
    <instruction>2. Use 'None' for exports, imports, and external_dependencies if there are none.</instruction>
    <instruction>3. Omit the external_dependencies tag if there are no external dependencies.</instruction>
    <instruction>4. Respond strictly with the XML structure; no additional text.</instruction>
  </guidelines>
  <metadata>
    <path>{filename}</path>
    <type>file_type</type>
    <summary>Brief description of the file's purpose and functionality</summary>
    <file_category>code_file or dependency_file</file_category>
    <exports>Comma-separated list of exports or 'None'</exports>
    <imports>Comma-separated list of imports or 'None'</imports>
    <!-- Include external_dependencies tag only if there are external dependencies -->
    <external_dependencies>
      <dependency>
        <name>name1</name>
        <version>version1</version>
      </dependency>
    </external_dependencies>
  </metadata>
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
"""