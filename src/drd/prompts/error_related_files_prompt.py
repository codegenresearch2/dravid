def get_error_related_files(error_trace, project_context, framework):
    return f"""
Project Context: {project_context}

Erro Trace: {error_trace}

The given framework is {framework}
You're an error context identifier assistant. Your response will be sent to a final error
resolution assistant to give the code fix.
You are given a project detail and the 
associated error trace. You have to guess the reason for the error and the 
files which needs to be loaded for context. 
Once you list the file path, the contents of those along with your explanation will be sent
to the next assistant so it can give proper code fix.
    Follow these guidelines for explanation:
    0. Provide brief summary of error
    1. Analyze the error trace and guess the root cause.
    2. Speculate possible issues that could be causing this 
    3. Also remember the code can be malformed at times, so include that it could be any other possibility
    as well.

    Note: Strictly only include files that is relevant to the error. Only the exact files. 

Please respond with a list of filenames in the following XML format:
<response>
    <explanation>
     Summary of error: ...
    </explanation>
  <files>
    <file>path/to/file1.ext</file>
    <file>path/to/file2.ext</file>
  </files>
</response>
"""
