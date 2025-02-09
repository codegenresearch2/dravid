def get_instruction_prompt():
    return """
    <response>
      <explanation>This prompt provides detailed instructions for setting up a project, including creating new projects like Next.js, Rails, or Python apps, and managing file operations relative to the current directory. It also emphasizes the importance of following best practices and maintaining accurate project metadata.</explanation>
      <steps>
        <step>
          <type>shell</type>
          <command>npx create-next-app@latest .</command>
        </step>
        <step>
          <type>file</type>
          <operation>CREATE</operation>
          <filename>app.js</filename>
          <content>
            <![CDATA[
              function example() {
                console.log('Hello, world!');
              }
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
                    "filename": "app.js",
                    "type": "JavaScript",
                    "description": "...",
                    "exports": "None"
                  }
                ],
                "dev_server": {
                  "start_command": "node app.js",
                  "framework": "express",
                  "language": "javascript"
                }
              }
            ]]>
          </content>
        </step>
      </steps>
    </response>
    """