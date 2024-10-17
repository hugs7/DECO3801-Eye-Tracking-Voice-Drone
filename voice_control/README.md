# Drone Voice Control

This module handles voice recognition and command translation via an LLM to convert voice into drone commands.

## Getting started

### 1. Package Dependencies

Install the requirements via the following command from a command prompt in the root directory of the project.

```bash
pip install -r voice_control/requirements.txt
```

### 2. Additional Dependencies

The voice control module also requires ffmpeg to handle in-app sounds. This library is not available via pip. For Windows, you can install this by visiting [ffmpeg-builds on GitHub](https://github.com/BtbN/FFmpeg-Builds/releases) and downloading the latest `win64` release. At the time of writing, that is [2024-09-15 13:01](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip) but there are releases daily for this software.

Once downloaded, unzip the folder then move the contents into `C:\Program Files\ffmpeg\`. You should have something like `C:\Program Files\ffmpeg\ffmpeg-2024-09-15`, with the date changed depending upon your build. Note you don't have to place it here, but it is convenient and makes sense for most setups.

Open the start menu and type `Env` then press Enter. Click `Environment Variables` and under **System Variables**, double-click on **Path**. Click New then browse to the `/bin/` folder of ffmpeg. E.g. `C:\Program Files\ffmpeg\ffmpeg-2024-09-15\bin\`. Click `OK` > `OK` > `OK`.

**Ensure you restart your terminal (or computer) after installation.** Drone Voice Control will work without it, however, sound effects will not.

### 3. OpenAI Key

Add your OpenAI API key in `voice_control/.env` as

```
OPENAI_API_KEY=...
```

### 4. LLM Data

Add context and prompt information (used by the NLU/LLM in order to process the voice commands in a desirable manner). You can download the data folder used in development at [this Google Drive folder](https://drive.google.com/drive/folders/1vTnuQttrPQ0hgq_KUsqppmDC-xUoEvJI?usp=sharing]). Once downloaded, unzip and place at `/voice_control/data`, ensuring there is no sub-data folder within it. That is, you should have defined the following files.

-   `/voice_control/data/context.jsonl`: Stores updated contextual information about the problem during model evaluation.
-   `/voice_control/data/initial.jsonl`: Used for training the model, but not used during evaluation.
-   `/voice_control/data/system_prompt.txt`: Defines the prompt provided to the LLM for how to respond when it is provided with your voice command.

### 5. Run the main script.

```bash
python voice_control/main.py
```

You can also run in module mode via the following. The main file at `voice_control/main.py` is simply a wrapper for the `src/main.py` file which enables running in standard mode.

```bash
python -m voice_control.src.main
```

## Using the Voice Control Module

1. As defined in the config file `/voice_control/configs/config.yaml`, under `audio > wake command`, the command specified to activate voice control is defined. Once the application is running, you can say this command and, if enabled, a wake sound will play to signify it is listening to your next command.

2. Say a command into the microphone for what you would like the drone to do. E.g. you can say _"Takeoff then go forwards 50 metres"_.

3. The application will play a sound to signify the command is accepted (if enabled), and if `send_to_llm` (see below) is enabled in the configuration, the text version of your command will be sent to OpenAI to process words into commands understandable by the drone. If running in standalone, the result is discarded, but in threadding mode, the resultant command is shared with the drone controller thread and sent to the drone to perform.

4. The above three steps are defined in a loop and will repeat until the application is quit. The app is always listening for your wake command, and won't respond to voice if it is not said after the wake command.

## Configuration Settings

This module has various configuration settings which are defined below.

### `voice_control`

-   **`use_existing_recording`** (`bool`): If `True`, uses a pre-existing recording for voice recognition instead of capturing new audio.
-   **`detect_voice`** (`bool`): If `True`, enables voice detection for user commands. If disabled, user will be prompted via a text input in the console.
-   **`send_to_llm`** (`bool`): If `True`, sends your voice command (as converted to text) to the LLM to be converted into a format understandable by the drone controller. When running in standalone, the result is discarded, but when running in threadded mode, the result is added to the queue at `thread_data["voice_control"]["command_queue"]`. If `False`, it is not required for the user to define their `OPENAI_API_KEY` in their `.env` file.

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
