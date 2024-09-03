import os
import openai
from colorama import Fore
from typing import List, Dict
from core import AgentInteractiveConsole, react
from defaults import initial_context
from utils import log
from wrappers import done, proxy_input
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_API_KEY")
assert openai.api_key is not None, "Please assign a valid OpenAI API key to the environment variable OPENAI_API_KEY."


def ask_fn(context: List[Dict[str, str]], aux: bool = False) -> str:
	model = "gpt-4o-mini"#model = "gpt-3.5-turbo" #if aux else "gpt-4o-mini"
	response = openai.ChatCompletion.create(model=model, temperature=0, messages=context)
	return response["choices"][0]["message"]["content"]


def run_terminal_agent(user_input) -> str:
	interactive_console = AgentInteractiveConsole(locals={"done": done, "input": proxy_input})
	context = initial_context
	if (user_input == "train"):
		while (user_input := input("Enter a message (or exit to quit): ")) != "exit":
			user_command = f">>> # User: {user_input}"
			react(interactive_console, ask_fn, context, user_command)
		
	else:
		user_command = f">>> # User: {user_input}"
		_, _, output = react(interactive_console, ask_fn, context, user_command)
		return output
			
	log("--- The simulation has ended ---", color=Fore.LIGHTRED_EX)


if __name__ == "__main__":
	run_terminal_agent("")
