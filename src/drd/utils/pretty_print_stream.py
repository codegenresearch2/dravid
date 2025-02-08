import re
import click


def pretty_print_xml_stream(chunk, state):
    state['buffer'] += chunk

    max_iterations = 1000
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        if not state.get('in_step'):
            # Process explanation tags
            match = re.search(r'<
*explanation
*>.*?<
*/explanation
*>', state['buffer'], re.DOTALL | re.IGNORECASE)
            if match:
                explanation = match.group(1).strip()
                click.echo(click.style('\nExplanation:', fg='green', bold=True), nl=False)
                click.echo(f' {explanation}')
                state['buffer'] = state['buffer'][match.end():]
                continue

            # Look for step start
            step_start = re.search(r'<
*step
*>', state['buffer'], re.IGNORECASE)
            if step_start:
                state['in_step'] = True
                state['buffer'] = state['buffer'][step_start.end():]
                continue

        if state['in_step']:
            step_end = re.search(r'<
*/step
*>', state['buffer'], re.IGNORECASE)
            if step_end:
                step_content = state['buffer'][:step_end.start()]
                state['buffer'] = state['buffer'][step_end.end():]
                state['in_step'] = False

                # Process step content
                type_match = re.search(r'<
*type
*>.*?<
*/type
*>', step_content, re.DOTALL | re.IGNORECASE)
                if type_match:
                    step_type = type_match.group(1).strip().lower()
                    if step_type == 'file':
                        operation_match = re.search(r'<
*operation
*>.*?<
*/operation
*>', step_content, re.DOTALL | re.IGNORECASE)
                        filename_match = re.search(r'<
*filename
*>.*?<
*/filename
*>', step_content, re.DOTALL | re.IGNORECASE)
                        if operation_match and filename_match:
                            operation = operation_match.group(1).strip()
                            filename = filename_match.group(1).strip()
                            click.echo(click.style('\n📂 File Operation:', fg='yellow', bold=True), nl=False)
                            click.echo(f' {operation} {filename}')

                            # Process CDATA content
                            cdata_start = step_content.find('<![CDATA[')
                            if cdata_start != -1:
                                cdata_end = step_content.rfind(']]>')
                                if cdata_end != -1:
                                    cdata_content = step_content[cdata_start+9:cdata_end]
                                    click.echo(click.style('\n📄 File Content:', fg='cyan', bold=True))
                                    click.echo(cdata_content)
                    elif step_type == 'shell':
                        command_match = re.search(r'<
*command
*>.*?<
*/command
*>', step_content, re.DOTALL | re.IGNORECASE)
                        if command_match:
                            command = command_match.group(1).strip()
                            click.echo(click.style('\n🐚 Shell Command:', fg='blue', bold=True), nl=False)
                            click.echo(f' {command}')
                continue

        # If we've reached this point, we couldn't process anything in this iteration
        break

    if iteration_count == max_iterations:
        print('Debug: Max iterations reached, possible infinite loop detected')



def stream_and_print_commands(chunks):
    state = {
        'buffer': '',
        'in_step': False,
    }

    for chunk in chunks:
        pretty_print_xml_stream(chunk, state)

    if state['buffer'].strip():
        click.echo(f'\n📄 Remaining Content: {state['buffer'].strip()}')

    click.echo()
