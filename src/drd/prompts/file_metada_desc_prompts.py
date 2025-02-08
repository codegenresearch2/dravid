def get_file_metadata_prompt(filename, content, project_context, folder_structure):\n    return f"""\n{project_context}\nCurrent folder structure:\n{folder_structure}\nFile: {filename}\nContent:\n{content}\n\nYou're the project context maintainer. Your role is to keep relevant meta info about the entire project \ns so it can be used by an AI coding assistant in future for reference.\n\nBased on the file content, project context, and the current folder structure, \nplease generate appropriate metadata for this file. \n\nIf this file appears to be a dependency management file (like package.json, requirements.txt, Cargo.toml, etc.),\nprovide a list of external dependencies. \n\nIf it's a code file, provide a summary, list of exports (functions, classes, or variables available for importing),\nand a list of imports from other project files. \n\nRespond with an XML structure containing the metadata:\n\n<response>\n  <metadata>\n    <type>file_type</type>\n    <summary>Description based on the file's contents, project context, and folder structure</summary>\n    <category>code_file or dependency_file</category>\n    <exports>fun:functionName,class:ClassName,var:variableName</exports>\n    <imports>path/to/file:importedName</imports>\n    <external_dependencies>\n      <dependency>\n        <dependency>name1@version1</dependency>\n        <dependency>name2@version2</dependency>\n    </external_dependencies>\n  </metadata>\n</response>\n\nRespond strictly only with the XML response as it will be used for parsing, no other extra words. \nIf there are no exports, use <exports>None</exports> instead of an empty tag. \nIf there are no imports, use <imports>None</imports> instead of an empty tag. \nIf there are no external dependencies, omit the <external_dependencies> tag entirely. \nEnsure that all other tags (type, summary, category, exports, imports) are always present and non-empty."""\n