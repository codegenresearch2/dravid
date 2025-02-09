<response>
  <explanation>A brief explanation of the steps, if necessary</explanation>
  <steps>
    <step>
      <type>shell</type>
      <command>npx create-next-app@latest .</command>
    </step>
    <step>
      <type>file</type>
      <operation>UPDATE</operation>
      <filename>app.py</filename>
      <content>
        <![CDATA[
          + 3: import new_module
          - 10:
          r 15: def updated_function():
        ]]> 
      </content>
    </step>
    <step>
      <type>metadata</type>
      <operation>UPDATE_FILE</operation>
      <filename>drd.json</filename>
      <content>
        <![CDATA[
          {}
        ]]> 
      </content>
    </step>
    <step>
      <type>metadata</type>
      <operation>UPDATE</operation>
      <filename>drd.json</filename>
      <content>
        <![CDATA[
          {}
        ]]> 
      </content>
    </step>
  </steps>
</response>