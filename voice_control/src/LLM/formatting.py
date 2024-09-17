"""
Module for formatting code and terminal entries.
"""

from typing import List, Dict, Callable

from ..constants import PYTHON_PROMPT, CONTINUATION_PROMPT, PYTHON_SHELL, ELLIPSIS


def remove_terminal_line_decorators(terminal_code: str) -> str:
    """
    Removes terminal line decorators (e.g., '>>> ' and '... ') from the given terminal code.

    Args:
        terminal_code (str): A string representing code with terminal line decorators.

    Returns:
        str: The terminal code with the decorators removed.
    """
    terminal_trimmed = "\n".join([line[4:] if line.startswith(
        (PYTHON_PROMPT, CONTINUATION_PROMPT)) else line for line in terminal_code.splitlines()])
    return terminal_trimmed.strip()


def remove_code_block_formatting(code: str) -> str:
    """
    Removes triple backticks and language markers from the code, such as ```python and ```.

    Args:
        code (str): The code possibly containing triple backticks.

    Returns:
        str: The code without code block markers.
    """
    return code.replace("```python", "").replace("```", "").strip()


def add_terminal_line_decorators(terminal_entry: str) -> str:
    """
    Adds terminal line decorators ('>>> ' for the first line and '... ' for subsequent lines) 
    to the given terminal code.

    Args:
        terminal_entry (str): A string representing a block of code without terminal line decorators.

    Returns:
        str: The code with appropriate terminal line decorators added.
    """
    decorated_lines = list()
    for i, line in enumerate(terminal_entry.splitlines()):
        decoration = PYTHON_PROMPT if i == 0 else CONTINUATION_PROMPT
        decorated_lines.append(decoration + line)
    return "\n".join(decorated_lines)


def ensure_terminal_formatting_strict(terminal_code: str, force: bool = False) -> str:
    """
    Ensures that the given terminal code follows strict terminal formatting rules:
    - Lines must start with '>>> ' or '... '.
    - Empty lines and invalid formatting will be ignored or raise an assertion.

    Args:
        terminal_code (str): The code to check and enforce terminal formatting on.
        force (bool, optional): If True, it will skip non-terminal formatted lines. Defaults to False.

    Returns:
        str: The strictly formatted terminal code.

    Raises:
        AssertionError: If a line does not follow the terminal formatting rules.
    """
    formatted_lines = list()
    for i, line in enumerate(terminal_code.splitlines()):
        if not line:
            continue

        if line[0] == "#":
            line = PYTHON_PROMPT + line

        if line in {PYTHON_SHELL, ELLIPSIS}:
            line += " "

        if force and line[:len(CONTINUATION_PROMPT)] not in {PYTHON_PROMPT, CONTINUATION_PROMPT}:
            continue

        formatted_lines.append(line)
    return "\n".join(formatted_lines)


def ensure_terminal_formatting_llm(code: str, ask_fn: Callable[[List[Dict[str, str]], bool], str]) -> str:
    """
    Ensures the terminal formatting of the code using a language model, by prompting the LLM to format it correctly.

    Args:
        code (str): The code to be formatted.
        ask_fn (Callable[[List[Dict[str, str]], bool], str]): A function to interact with the LLM to format the code.

    Returns:
        str: The code formatted with terminal-style decorators.
    """
    formatting_prompt = (
        "Format the following code as if it was code written in a python terminal. The output must comply with these "
        "rules:\n"
        "- Every line has to start with either `>>>` or `...`.\n"
        "- There can't be any blank line.\n"
        "- There can only be valid python commands or comments.\n"
        "If you find free-form text, convert it into a comment.\n\n"
        f"```\n{code}\n```"
    )
    return ask_fn([{"role": "user", "content": formatting_prompt}], True).strip()


def ensure_terminal_formatting(code: str, ask_fn: Callable[[List[Dict[str, str]], bool], str]) -> str:
    """
    Ensures that the given code is properly formatted for a terminal. First tries strict formatting,
    and if that fails, falls back to using the LLM to reformat the code.

    Args:
        code (str): The code to format.
        ask_fn (Callable[[List[Dict[str, str]], bool], str]): The LLM function to ask for formatting help if needed.

    Returns:
        str: The formatted terminal code.

    Side Effects:
        Sometimes, the LLM hallucinates output lines if `print` is on the last line.
    """
    try:
        return ensure_terminal_formatting_strict(code)
    except AssertionError:
        pass
    llm_formatted_code = ensure_terminal_formatting_llm(code, ask_fn)

    num_code_lines = len(code.splitlines())
    llm_formatted_code = "\n".join(
        llm_formatted_code.splitlines()[:num_code_lines])
    return ensure_terminal_formatting_strict(llm_formatted_code, force=True)


def extract_terminal_entries(terminal_code: str) -> List[str]:
    """
    Extracts code entries from terminal-formatted code by splitting it based on '>>> ' markers,
    and removes terminal line decorators.

    Args:
        terminal_code (str): The terminal-formatted code with line decorators (e.g., '>>> ' and '... ').

    Returns:
        List[str]: A list of extracted and cleaned code entries.
    """

    entries = terminal_code.split("\n" + PYTHON_PROMPT)
    entries = [PYTHON_PROMPT + e if i >
               0 else e for i, e in enumerate(entries)]

    return [remove_terminal_line_decorators(e) for e in entries]
