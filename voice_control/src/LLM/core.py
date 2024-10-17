"""
Core functionality for interacting with the language model and executing code in the agent's environment.
"""

from typing import List, Tuple, Dict, Callable
import json
import os
import contextlib
from io import StringIO
from code import InteractiveConsole

from common.logger_helper import init_logger

from .wrappers import AgentIsDone
from .utils import ask_llm
from .formatting import add_terminal_line_decorators, extract_terminal_entries

from common import str_helper

from ..file_handler import get_context_file
from ..constants import MAX_LOOP


logger = init_logger()


class AgentInteractiveConsole(InteractiveConsole):
    """
    A custom interactive console for executing code within an agent's environment.

    This class extends the standard `InteractiveConsole` and overrides the `runcode` method
    to handle specific exceptions such as `SystemExit` and `AgentIsDone`. Other exceptions are
    caught and displayed using the built-in traceback display mechanism.

    Methods:
        runcode(code):
            Executes the given code in the console's local environment and handles exceptions.
    """

    def runcode(self, code) -> None:
        """
        Executes the provided code within the console's local namespace.

        This method attempts to execute the provided code. If a `SystemExit` or `AgentIsDone`
        exception is raised, it is propagated. For any other exceptions, the traceback is displayed.

        Args:
            code (str): The code to execute.

        Raises:
            SystemExit: Propagated if a system exit is triggered.
            AgentIsDone: Propagated if the agent's task is completed.

        Returns:
            None
        """
        try:
            exec(code, self.locals)
        except (SystemExit, AgentIsDone):
            raise
        except:
            self.showtraceback()


def run_entry(interactive_console: AgentInteractiveConsole, entry_code: str) -> Tuple[bool, str, str, str]:
    """
    Executes a given code entry in the agent's interactive console and captures the output.

    This function takes an interactive console and a block of code (as a string), executes
    the code line by line, and captures any output from stdout and stderr. It also handles
    the special case where the agent indicates it is done via an `AgentIsDone` exception.

    Args:
        interactive_console (AgentInteractiveConsole): The interactive console where the code will be executed.
        entry_code (str): The code to be executed, provided as a multi-line string.

    Returns:
        Tuple[bool, str, str, str]:
            - bool: A flag indicating if the agent has completed its task (`True` if `AgentIsDone` was raised).
            - str: The captured output from stdout and stderr during the execution.
            - str: The executed lines of code, decorated with terminal formatting.
            - str: Any additional message, empty if no specific message is generated.

    Exceptions:
        AgentIsDone: If raised during code execution, the `agent_is_done` flag is set to `True`.
    """
    interactive_console.resetbuffer()
    message = ""
    agent_is_done = False
    executed_lines = []
    with StringIO() as redirected_stdout_stderr:
        with contextlib.redirect_stdout(redirected_stdout_stderr):
            with contextlib.redirect_stderr(redirected_stdout_stderr):
                try:
                    more_input = False
                    for line in entry_code.splitlines():
                        executed_lines.append(line)
                        more_input = interactive_console.push(line)
                        if not more_input:
                            break
                    if more_input:
                        interactive_console.push("")
                except AgentIsDone:
                    agent_is_done = True
        executed_lines = add_terminal_line_decorators(
            "\n".join(executed_lines))
        return (
            agent_is_done,
            redirected_stdout_stderr.getvalue().strip(),
            executed_lines,
            message,
        )


def correct_format(response: str) -> bool:
    """
    Checks if the given string can be safely evaluated into a list of tuples.

    This function attempts to evaluate the provided string using `eval()` and verifies whether
    the result is a list where every element is a tuple. If the evaluation fails or the result
    does not match the expected format, it returns `False`.

    Args:
        response (str): A string representation of a Python object, expected to evaluate to a list of tuples.

    Returns:
        bool: `True` if the string evaluates to a list of tuples, otherwise `False`.

    Exceptions:
        Any exceptions raised during evaluation will be caught, and the function will return `False`.
    """
    try:
        eval_response = eval(response)
        return isinstance(eval_response, list) and all(isinstance(i, tuple) for i in eval_response)
    except:
        return False


def run_until_halt(
    interactive_console: AgentInteractiveConsole,
    ask_fn: Callable[[List[Dict[str, str]], bool], str],
    context: List[Dict[str, str]],
) -> Tuple[bool, str]:
    """
    Continuously executes code provided by a language model until an agent signals completion or a valid output is produced.

    This function loops, requesting code from an LLM through `ask_fn`, and executes it in the provided `interactive_console`.
    It appends the executed code and any captured output to the context, which is used to inform further requests to the LLM.
    The loop breaks when the agent signals it is done via an `AgentIsDone` exception or a correctly formatted output is generated.

    Args:
        interactive_console (AgentInteractiveConsole): The console in which the code entries will be executed.
        ask_fn (Callable): A function to call the LLM, expecting the current context and a boolean to guide the request.
        context (List[Dict[str, str]]): The conversation context between the user and the assistant, updated throughout execution.

    Returns:
        Tuple[bool, str]:
            - bool: A flag indicating if the agent has completed its task (`True` if `AgentIsDone` was raised).
            - str: The last captured output from the execution, which will either be valid or signal that execution has stopped.

    Behavior:
        - The function queries the LLM for code, executes it in the `interactive_console`, and logs the output.
        - It continues execution until either the agent signals it is done or valid output is received.
    """
    agent_is_done = False
    message = ""
    loop_count = 0
    while not (agent_is_done or message != "") and loop_count < MAX_LOOP:
        captured_output = ""
        executed_entries = list()

        terminal_code = ask_llm(context, ask_fn)

        terminal_entries = extract_terminal_entries(terminal_code)

        for entry_code in terminal_entries:
            (
                agent_is_done,
                captured_output,
                executed_lines,
                message,
            ) = run_entry(interactive_console, entry_code)
            executed_entries.append(executed_lines)
            # As soon as there's some output, the LLM might want to react to it -> put it in context and ask again.
            logger.info("Captured output: %s",
                        str_helper.trim(captured_output))
            if agent_is_done or captured_output != "":
                break

        executed_code = "\n".join(executed_entries)
        context.append({"role": "assistant", "content": executed_code})
        logger.info("Executed code: %s", str_helper.trim(executed_code))
        if captured_output != "":
            context.append({"role": "user", "content": captured_output})
            logger.info("Captured output: {str_helper.trim(captured_output)}")
            if correct_format(captured_output):
                break

        loop_count += 1

    if loop_count >= MAX_LOOP:
        logger.warning("Max loop count %s reached", MAX_LOOP)

    return agent_is_done, message, captured_output


def react(
    interactive_console: AgentInteractiveConsole,
    ask_fn: Callable[[List[Dict[str, str]], bool], str],
    context: List[Dict[str, str]],
    user_command: str,
) -> Tuple[bool, str]:
    """
    Handles user commands by updating context, saving it, and interacting with the LLM until a task is completed or output is produced.

    This function processes a user command, stores it in a context file, and then appends it to the provided `context`.
    The context is used to query the LLM via `ask_fn` and execute responses using the `interactive_console`.
    It continues interacting with the LLM until the agent signals completion or produces valid output.

    Args:
        interactive_console (AgentInteractiveConsole): The console in which LLM-provided code entries will be executed.
        ask_fn (Callable): A function for querying the LLM, providing the current context and a boolean parameter.
        context (List[Dict[str, str]]): The conversation history and context between the user and the assistant.
        user_command (str): The command provided by the user to be processed.

    Returns:
        Tuple[bool, str]:
            - bool: A flag indicating whether the agent has completed its task (`True` if `AgentIsDone` was raised).
            - str: The last message from the agent or an empty string if there is no specific message.
            - str: The final output produced by the execution, if available.

    Behavior:
        - The function first reads from the context file (if it exists), appends the user command, and saves the updated context.
        - It then logs and updates the context before invoking `run_until_halt` to interact with the LLM and execute code.
        - The function runs until the agent completes its task or produces an actionable output.

    Side effects:
        - Modifies the context file by appending the user command and the ongoing conversation context.
    """
    context_file = get_context_file()
    stored_context = []

    if os.path.exists(context_file) and os.path.getsize(context_file) > 0:
        with open(context_file, "r") as f:
            for line in f:
                parsed = json.loads(line)
                stored_context.append(parsed)

    stored_context.append({"role": "user", "content": user_command})
    with open(context_file, "w") as f:
        for entry in stored_context:
            f.write(json.dumps(entry) + "\n")

    logger.info(user_command)
    context.append({"role": "user", "content": user_command})
    agent_is_done, message, output = run_until_halt(
        interactive_console, ask_fn, stored_context)
    return agent_is_done, message, output
