def get_instruction_prompt():
    return """
    <response>
      <explanation>
        This prompt generates production-grade instructions for various programming projects.
        It follows best practices for each language and framework.
        Steps are generated in the proper order, with prerequisite steps first to avoid errors.
        The current directory is used for all operations, including creating new projects.
        Additional safe directories are allowed.
        Command execution safety checks are enhanced.
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
          <filename>new_file.py</filename>
          <content>
            <![CDATA[
              def example():
                # Function content...
            ]]>
          </content>
        </step>
        <step>
          <type>file</type>
          <operation>UPDATE</operation>
          <filename>existing_file.py</filename>
          <content>
            <![CDATA[
              + 3: import new_module
              - 10:
              r 15: def updated_function():
            ]]>
          </content>
        </step>
        <step>
          <type>file</type>
          <operation>DELETE</operation>
          <filename>file_to_delete.py</filename>
        </step>
        <step>
          <type>metadata</type>
          <operation>UPDATE_FILE</operation>
          <filename>drd.json</filename>
          <content>
            <![CDATA[
              {
                "dev_server": {
                  "start_command": "python start",
                  "framework": "flask",
                  "language": "python"
                }
              }
            ]]>
          </content>
        </step>
      </steps>
      <requires_restart>true</requires_restart>
    </response>
    """