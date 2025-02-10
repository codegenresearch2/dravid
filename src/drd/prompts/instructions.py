def get_instruction_prompt():
    return """
    <response>
      <explanation>
        This prompt generates production-grade instructions for setting up various programming projects.
        It follows best practices for each language and framework, and uses the current directory for all operations.
        The output is in XML format.
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
                print('Hello, World!')
            ]]>
          </content>
          <explanation>Creates a new Python file with a simple function.</explanation>
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
          <explanation>Updates an existing Python file with specific changes.</explanation>
        </step>
        <step>
          <type>file</type>
          <operation>DELETE</operation>
          <filename>file_to_delete.py</filename>
          <explanation>Deletes a specified file.</explanation>
        </step>
        <step>
          <type>metadata</type>
          <operation>UPDATE_FILE</operation>
          <filename>drd.json</filename>
          <content>
            <![CDATA[
              // JSON content to update the project metadata
            ]]>
          </content>
          <explanation>Updates the project metadata file.</explanation>
        </step>
      </steps>
      <requires_restart>false</requires_restart>
    </response>
    """