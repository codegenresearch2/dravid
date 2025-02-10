def get_instruction_prompt():
    return """
    <response>
      <explanation>
        This assistant generates production-grade instructions for various programming projects, focusing on best practices for each language and framework. It provides steps for project initialization, file creation, modification, and deletion, with prerequisite steps listed first.
      </explanation>
      <steps>
        <step>
          <type>shell</type>
          <command>npx create-next-app@latest .</command>
          <explanation>Creates a new Next.js project in the current directory.</explanation>
        </step>
        <step>
          <type>file</type>
          <operation>CREATE</operation>
          <filename>new_file.js</filename>
          <content>
            <![CDATA[
              // Content of the new file...
            ]]>
          </content>
        </step>
        <step>
          <type>file</type>
          <operation>UPDATE</operation>
          <filename>existing_file.js</filename>
          <content>
            <![CDATA[
              + line_number: content to add
              - line_number: (to remove the line)
              r line_number: content to replace the line with
            ]]>
          </content>
        </step>
        <step>
          <type>file</type>
          <operation>DELETE</operation>
          <filename>file_to_delete.js</filename>
        </step>
        <step>
          <type>metadata</type>
          <operation>UPDATE_FILE</operation>
          <filename>drd.json</filename>
          <content>
            <![CDATA[
              {
                "dev_server": {
                  "start_command": "npm run dev",
                  "framework": "Next.js",
                  "language": "JavaScript"
                }
              }
            ]]>
          </content>
        </step>
      </steps>
      <requires_restart>false</requires_restart>
    </response>
    """

# Test the function
print(get_instruction_prompt())