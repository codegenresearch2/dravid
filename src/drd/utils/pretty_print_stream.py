import re
import click

def pretty_print_xml_stream(chunk, state):
    # Append the chunk to the buffer
    state['buffer'] += chunk

    max_iterations = 1000
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        # Check if we're currently processing a step
        if not state.get('in_step'):
            # Try to find and process an explanation tag
            explanation_match = re.search(r'<\s*explanation\s*>(.*?)<\s*/\s*explanation\s*>', state['buffer'], re.DOTALL | re.IGNORECASE)
            if explanation_match:
                # Print the explanation and remove it from the buffer
                click.echo(click.style("\n📝 Explanation:", fg="green", bold=True), nl=False)
                click.echo(f" {explanation_match.group(1).strip()}")
                state['buffer'] = state['buffer'][explanation_match.end():]
                continue

            # Look for the start of a step tag
            step_start = re.search(r'<\s*step\s*>', state['buffer'], re.IGNORECASE)
            if step_start:
                # Set the in_step flag and remove the step start tag from the buffer
                state['in_step'] = True
                state['buffer'] = state['buffer'][step_start.end():]
                continue

        # If we're processing a step, try to find the end of the step tag
        if state['in_step']:
            step_end = re.search(r'<\s*/\s*step\s*>', state['buffer'], re.IGNORECASE)
            if step_end:
                # Extract the step content and remove it from the buffer
                step_content = state['buffer'][:step_end.start()]
                state['buffer'] = state['buffer'][step_end.end():]
                state['in_step'] = False

                # Try to find and process the type of the step
                type_match = re.search(r'<\s*type\s*>(.*?)<\s*/\s*type\s*>', step_content, re.DOTALL | re.IGNORECASE)
                if type_match:
                    step_type = type_match.group(1).strip().lower()
                    if step_type == 'file':
                        # Extract the operation and filename and print them
                        operation_match = re.search(r'<\s*operation\s*>(.*?)<\s*/\s*operation\s*>', step_content, re.DOTALL | re.IGNORECASE)
                        filename_match = re.search(r'<\s*filename\s*>(.*?)<\s*/\s*filename\s*>', step_content, re.DOTALL | re.IGNORECASE)
                        if operation_match and filename_match:
                            click.echo(click.style("\n📂 File Operation:", fg="yellow", bold=True), nl=False)
                            click.echo(f" {operation_match.group(1).strip()} {filename_match.group(1).strip()}")

                        # Try to find and print CDATA content
                        cdata_start = step_content.find("<![CDATA[")
                        if cdata_start != -1:
                            cdata_end = step_content.rfind("]]>")
                            if cdata_end != -1:
                                cdata_content = step_content[cdata_start+9:cdata_end]
                                click.echo(click.style("\n📄 File Content:", fg="cyan", bold=True))
                                click.echo(cdata_content)
                    elif step_type == 'shell':
                        # Extract and print the shell command
                        command_match = re.search(r'<\s*command\s*>(.*?)<\s*/\s*command\s*>', step_content, re.DOTALL | re.IGNORECASE)
                        if command_match:
                            click.echo(click.style("\n💻 Shell Command:", fg="blue", bold=True), nl=False)
                            click.echo(f" {command_match.group(1).strip()}")
                continue

        # If we've reached this point, we couldn't process anything in this iteration
        break

    # Print a debug message if we've reached the maximum number of iterations
    if iteration_count == max_iterations:
        print("Debug: Max iterations reached, possible infinite loop detected")

def stream_and_print_commands(chunks):
    # Initialize the state
    state = {'buffer': '', 'in_step': False}

    # Process each chunk
    for chunk in chunks:
        pretty_print_xml_stream(chunk, state)

    # Print any remaining content in the buffer
    if state['buffer'].strip():
        click.echo(f"\nRemaining Content: {state['buffer'].strip()}")

    # Print a final newline
    click.echo()