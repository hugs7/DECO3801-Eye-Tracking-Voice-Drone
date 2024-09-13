# Drone Voice Control

This module handles voice recognition and command translation via an LLM to convert voice into drone commands.

## Getting started

1. Install the requirements.

```bash
pip install -r voice_control/requirements.txt
```

2. Add your OpenAI API key in `voice_control/.env` as

```
OPENAI_API_KEY=...
```

3. Run the main script.

```bash
python voice_control/main.py
```

5. Speak into microphone
