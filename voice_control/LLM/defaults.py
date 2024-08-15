import json
import os
import ast

system_prompt = """
You are an assistant that exists within a python terminal. You help the user by writing python code. The user can read
everything you type or print. You can ask the user to do things for you, especially things that you cannot do, like
installing packages or rebooting the system. Use the `input` built-in function for that. Start all lines with `>>>` or
`...`, just like they read in the terminal. Very often you won't know things, so you are encouraged to help yourself by
calling built-in methods like `dir`, `vars` and others. Call `done()` when you are done.
""".strip().replace('\n', ' ')   

context_path = "voice_control\data\context.jsonl"
initial_path = "voice_control\data\initial.jsonl"
if os.path.exists(context_path) and os.path.getsize(context_path) > 0:
	with open(context_path, "r") as f:
		initial_context = [json.loads(line) for line in f]
	with open(initial_path, 'w') as f:
		for entry in initial_context:
			f.write(json.dumps(entry) + "\n")

	
else:
	initial_context = [{"role": "system", "content": system_prompt}]
	with open(initial_path, "r") as f:
		initial_context.extend(json.loads(line) for line in f)
	with open(context_path, 'w') as f:
		for entry in initial_context:
			f.write(json.dumps(entry) + "\n")
