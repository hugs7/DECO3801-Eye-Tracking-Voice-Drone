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

You can also run in module mode via the following. The main file at `voice_control/main.py` is simply a wrapper for the `src/main.py` file which enables running in standard mode.

```bash
python -m voice_control.src.main
```


## Configuration Settings

This module has various configuration settings which are defined below.

### `voice_control`

-   **`use_existing_recording`** (`bool`): If `True`, uses a pre-existing recording for voice recognition instead of capturing new audio.
-   **`detect_voice`** (`bool`): If `True`, enables voice detection for user commands.
-   **`send_to_llm`** (`bool`): If `True`, sends recognized voice commands to the language model (LLM) for further processing.

### `audio`

-   **`save_recordings`** (`bool`): If `True`, saves all voice recordings to a local folder.
-   **`wake_command`** (`string`): The phrase that the system listens for to activate voice input, e.g., "Ok Drone".
-   **`listen_timeout`** (`int`): The time in seconds to wait for voice input after the wake word has been detected.
-   **`phrase_time_limit`** (`int`): The maximum duration, in seconds, that the system will listen for a single voice command.
-   **`ambient_noise_duration`** (`float`): The duration, in seconds, to adjust for ambient noise before listening starts.
-   **`sound_effects`**:
    -   **`enable`** (`bool`): If `True`, enables sound effects when certain events (like wake word detection) occur.
    -   **`files`**: Contains file paths for sound effects:
        -   **`wake`** (`string`): Path to the sound file played when the wake word is detected (e.g., `sounds/wake.mp3`).
        -   **`accept`** (`string`): Path to the sound file played when a command is accepted (e.g., `sounds/accept.mp3`).
        -   **`reject`** (`string`): Path to the sound file played when a command is rejected (e.g., `sounds/reject.mp3`).

### `llm`

-   **`model`** (`string`): The language model to use, e.g., `gpt-4o-mini`.
-   **`temperature`** (`float`): Controls the randomness of the model's responses. A lower value (e.g., 0) makes the output more deterministic.
