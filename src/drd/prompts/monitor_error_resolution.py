# File: prompts/error_resolution_prompt.py
from .framework_prompts.main_frameworks_prompt import framework_specific_prompt


def get_error_resolution_prompt(error_trace, project_context, file_context=None, framework=None, user_feedback=None):
    framework_guidelines = framework_specific_prompt(framework)
    return f"""
    # Error Context
    An error occurred while running the server:

    Feedback: {user_feedback}

    Error summary:
    {error_trace}
   
    Project context:
    {project_context}

    File context: {file_context}
    # Instructions for dravid: Error Resolution Assistant
    Analyze the file contents and also the error above and provide steps to fix it.
    Note: The error summary is just an overview. 
    Evaluate the actual file for any syntax error as well apart from trying to fix the actual error.
    Don't try to do code refactoring or other changes unrelated to the error

    Framework: {framework}
    Framework specific guidelines: 
    {framework_guidelines}

    Important guidelines:
    1. Prioritize fixes in the main file where the error is reported.
    2. Avoid modifying dependencies or other files unless absolutely necessary. 
    For eg:
    There is a named export of a component or function but it is imported differently. 
    Prioritize fixing how it is imported over how it is exported as that maybe used referenced like that
    in other places.


    This is being run in a monitoring thread, so don't suggest server starting commands like npm run dev.
    Your response should be in strictly XML format with no other extra messages. Use the following format:
    <response>
    <explanation>A brief explanation of the steps, if necessary</explanation>
    <steps>
        <step>
        <type>shell</type>
        <command>command to execute</command>
        </step>
        <step>
        <type>file</type>
        <operation>CREATE</operation>
        <filename>path/to/file.ext</filename>
        <content>
            <![CDATA[
            file content here
            ]]>
        </content>
        </step>
       <step>
        <type>file</type>
        <operation>UPDATE</operation>
        <filename>path/to/existing/file.ext</filename>
        <content>
          <![CDATA[
          Specify changes using the following format:
          + line_number: content to add
          - line_number: (to remove the line)
          r line_number: content to replace the line with
          
          Example:
          + 3: import new_module
          - 10:
          r 15: def updated_function():
          ]]>
        </content>
      </step>
        <type>file</type>
        <operation>DELETE</operation>
        <filename>path/to/file/to/delete.ext</filename>
        </step>
    </steps>
    </response>
    """
