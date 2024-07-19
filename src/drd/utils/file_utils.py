import os
from .utils import print_info


def get_file_content(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            numbered_lines = [
                f"{i+1}: {line.rstrip()}" for i, line in enumerate(lines)]
            return "\n".join(numbered_lines)
    return None


def fetch_project_guidelines(project_dir):
    guidelines_path = os.path.join(project_dir, 'project_guidelines.txt')
    project_guidelines = ""
    if os.path.exists(guidelines_path):
        with open(guidelines_path, 'r') as guidelines_file:
            project_guidelines = guidelines_file.read()
        print_info("Project guidelines found and included in the context.")
    return project_guidelines
