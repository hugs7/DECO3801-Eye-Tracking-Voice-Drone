import openai
from colorama import Fore
from typing import List, Dict
from .core import AgentInteractiveConsole, react
from .defaults import init_context
from .wrappers import done, proxy_input
from constants import GPT_35_MODEL, GPT_4_MODEL
from .formatting import remove_code_block_formatting
import logging


logger = logging.getLogger(__name__)


def ask_fn(context: List[Dict[str, str]], aux: bool = False) -> str:
    """
    Sends a chat completion request to the OpenAI API using the specified model and returns the response.

    Args:
        context (List[Dict[str, str]]): A list of dictionaries representing the conversation history. 
                                        Each dictionary should contain keys like 'role' and 'content'.
        aux (bool, optional): A flag that determines whether to use the "gpt-3.5-turbo" model (if True) 
                              or "gpt-4o-mini" model (if False). Defaults to False.

    Returns:
        str: The content of the response from the OpenAI API.
    """
    model = GPT_35_MODEL if aux else GPT_4_MODEL
    response = openai.ChatCompletion.create(
        model=model, temperature=0, messages=context)
    terminal_code = response["choices"][0]["message"]["content"]
    clean_code = remove_code_block_formatting(terminal_code)
    return clean_code


def run_terminal_agent(user_input) -> str:
    """
    Runs an interactive terminal agent that reacts to user input and executes commands in a console environment.

    This function creates an interactive console, takes user input, and sends it to the agent to process. 
    It either continuously prompts the user for input or processes a single input if provided directly. 
    The agent's response is generated using a language model, which is invoked through the `react` function.

    Args:
        user_input (str): The initial user input. If empty, the function will prompt for user input interactively.

    Returns:
        str: The output generated by the agent in response to the user's command, if a non-empty input is provided.
             Otherwise, returns `None` as the user is interactively providing input.

    Behavior:
        - If `user_input` is an empty string, the function prompts the user for input continuously until "exit" is entered.
        - If `user_input` is provided, the function processes the command and returns the agent's output.

    Side Effects:
        - Logs the end of the simulation when the user exits.
        - Executes code in an `AgentInteractiveConsole` based on user input and LLM-generated responses.
    """
    interactive_console = AgentInteractiveConsole(
        locals={"done": done, "input": proxy_input})
    context = init_context()
    if (user_input == ""):
        while (user_input := input("Enter a message (or exit to quit): ")) != "exit":
            user_command = f">>> # User: {user_input}"
            react(interactive_console, ask_fn, context, user_command)
    else:
        user_command = f">>> # User: {user_input}"
        _, _, output = react(interactive_console, ask_fn,
                             context, user_command)
        return output

    logger.info("--- The simulation has ended ---", color=Fore.LIGHTRED_EX)


if __name__ == "__main__":
    run_terminal_agent("")