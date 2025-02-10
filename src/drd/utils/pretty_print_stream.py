import re
import click

def pretty_print_xml_stream(chunk, state):
    state['buffer'] += chunk

    while True:
        match = re.search(r'<\s*explanation\s*>(.*?)<\s*/\s*explanation\s*>', state['buffer'], re.DOTALL | re.IGNORECASE)
        if match:
            explanation = match.group(1).strip()
            click.echo(click.style("\nExplanation:", fg="green", bold=True), nl=False)
            click.echo(f" {explanation}")
            state['buffer'] = state['buffer'][match.end():]
            continue

        match = re.search(r'<\s*step\s*>', state['buffer'], re.IGNORECASE)
        if match:
            state['in_step'] = True
            state['buffer'] = state['buffer'][match.end():]
            continue

        if state['in_step']:
            step_end = re.search(r'<\s*/\s*step\s*>', state['buffer'], re.IGNORECASE)
            if step_end:
                step_content = state['buffer'][:step_end.start()]
                state['buffer'] = state['buffer'][step_end.end():]
                state['in_step'] = False

                type_match = re.search(r'<\s*type\s*>(.*?)<\s*/\s*type\s*>', step_content, re.DOTALL | re.IGNORECASE)
                if type_match and type_match.group(1).strip().lower() == 'file':
                    operation_match = re.search(r'<\s*operation\s*>(.*?)<\s*/\s*operation\s*>', step_content, re.DOTALL | re.IGNORECASE)
                    filename_match = re.search(r'<\s*filename\s*>(.*?)<\s*/\s*filename\s*>', step_content, re.DOTALL | re.IGNORECASE)
                    if operation_match and filename_match:
                        operation = operation_match.group(1).strip()
                        filename = filename_match.group(1).strip()
                        click.echo(click.style("\nFile Operation:", fg="yellow", bold=True), nl=False)
                        click.echo(f" {operation} {filename}")

                    cdata_start = step_content.find("<![CDATA[")
                    if cdata_start != -1:
                        cdata_end = step_content.rfind("]]>")
                        if cdata_end != -1:
                            cdata_content = step_content[cdata_start+9:cdata_end]
                            click.echo(click.style("\nFile Content:", fg="cyan", bold=True))
                            click.echo(cdata_content)
                elif type_match and type_match.group(1).strip().lower() == 'shell':
                    command_match = re.search(r'<\s*command\s*>(.*?)<\s*/\s*command\s*>', step_content, re.DOTALL | re.IGNORECASE)
                    if command_match:
                        command = command_match.group(1).strip()
                        click.echo(click.style("\nShell Command:", fg="blue", bold=True), nl=False)
                        click.echo(f" {command}")
                continue

        if not state['buffer'].strip():
            break

def stream_and_print_commands(chunks):
    state = {
        'buffer': '',
        'in_step': False,
    }

    for chunk in chunks:
        pretty_print_xml_stream(chunk, state)

    if state['buffer'].strip():
        click.echo(f"\nRemaining Content: {state['buffer'].strip()}")

    click.echo()