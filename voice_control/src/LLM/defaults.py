"""
This module contains the default values for the LLM model.
"""

import json
import os
import ast
from file_handler import get_data_folder, get_context_file


def init_context() -> list[dict]:
    """
    Initializes the context for the LLM model.

    This function reads the initial context from the 'context.jsonl' file in the 'data' folder.

    Returns:
        list[dict]: The initial context as a list of dictionaries
    """

    data_folder = get_data_folder()
    context_path = get_context_file()
    initial_path = os.path.join(data_folder, "initial.jsonl")

    if os.path.exists(context_path) and os.path.getsize(context_path) > 0:
        with open(context_path, "r") as f:
            initial_context = [json.loads(line) for line in f]
        with open(initial_path, 'w') as f:
            for entry in initial_context:
                f.write(json.dumps(entry) + "\n")
    else:
        system_prompt_path = os.path.join(data_folder, "system_prompt.txt")
        with open(system_prompt_path, 'r') as f:
            system_prompt = f.read().strip().replace('\n', ' ')

        initial_context = [{"role": "system", "content": system_prompt}]
        with open(initial_path, "r") as f:
            initial_context.extend(json.loads(line) for line in f)
        with open(context_path, 'w') as f:
            for entry in initial_context:
                f.write(json.dumps(entry) + "\n")

    return initial_context
