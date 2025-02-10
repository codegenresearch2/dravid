def get_instruction_prompt():
    return """
    <response>
      <explanation>
        This assistant generates production-grade instructions for various programming projects, following best practices for each language and framework. It generates steps in the proper order, with prerequisite steps first to avoid errors. The current directory is used for all operations, and additional safe directories are allowed. Command execution safety checks are enhanced.
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
          <filename>new_file.ext</filename>
          <content>
            <![CDATA[
              # Function or content to be added...
            ]]>
          </content>
        </step>
        <step>
          <type>file</type>
          <operation>UPDATE</operation>
          <filename>existing_file.ext</filename>
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
          <filename>file_to_delete.ext</filename>
        </step>
        <step>
          <type>metadata</type>
          <operation>UPDATE_FILE</operation>
          <filename>drd.json</filename>
          <content>
            <![CDATA[
              {
                "dev_server": {
                  "start_command": "command to start the server",
                  "framework": "framework used",
                  "language": "programming language used"
                }
              }
            ]]>
          </content>
        </step>
      </steps>
      <requires_restart>true/false</requires_restart>
    </response>
    """

# Test the function
print(get_instruction_prompt())