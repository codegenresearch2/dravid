def get_instruction_prompt():
    return """
    <response>
      <explanation>This XML response provides detailed instructions for setting up a project, including creating a new project like Next.js or Rails, and updating project metadata.</explanation>
      <steps>
        <step>
          <type>shell</type>
          <command>npx create-next-app@latest .</command>
        </step>
        <step>
          <type>file</type>
          <operation>CREATE</operation>
          <filename>app.py</filename>
          <content>
            <![CDATA[
              def example():
               re...
            ]]>
          </content>
        </step>
        <step>
          <type>metadata</type>
          <operation>UPDATE_FILE</operation>
          <filename>drd.json</filename>
          <content>
            <![CDATA[
              {
  "project_name": "pyser",
  "files": [
    {
      "filename": "app.py",
      "type": "Python",
      "description": "...",
      "exports": "None"
    },
    {
      "filename": "drd.json",
      "type": "json",
      "description": "",
      "exports": "None"
    }
  ],
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
    </response>
    """