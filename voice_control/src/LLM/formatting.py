from typing import List, Dict, Callable

def remove_terminal_line_decorators(terminal_code: str) -> str:
    """
    Removes terminal line decorators (e.g., '>>> ' and '... ') from the given terminal code.

    Args:
        terminal_code (str): A string representing code with terminal line decorators.

    Returns:
        str: The terminal code with the decorators removed.
    """
    return "\n".join([line[4:] for line in terminal_code.splitlines()])


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
        decoration = ">>> " if i == 0 else "... "
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
        if line == "":
            continue
        if line[0] == "#":
            line = ">>> " + line
        if line in {">>>", "..."}:
            line += " "
        if force and line[:4] not in {">>> ", "... "}:
            continue
        assert line[:4] in {">>> ", "... "}, f"Line {i} doesn't look like terminal code:\n{terminal_code}"
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
    """
    try:
        return ensure_terminal_formatting_strict(code)
    except AssertionError:
        pass
    llm_formatted_code = ensure_terminal_formatting_llm(code, ask_fn)
    # Sometimes, the LLM hallucinates output lines if `print` is on the last line.
    num_code_lines = len(code.splitlines())
    llm_formatted_code = "\n".join(llm_formatted_code.splitlines()[:num_code_lines])
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
    entries = terminal_code.split("\n>>> ")
    entries = entries[0:1] + [">>> " + e for e in entries[1:]]
    return [remove_terminal_line_decorators(e) for e in entries]
