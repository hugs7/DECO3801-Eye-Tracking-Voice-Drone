"""
Main module for the voice control program.
"""

import logging

import init
from LLM import run_terminal_agent
import logger_helper
import audio

root_logger = logger_helper.init_root_logger()


def process_voice_command(text: str):
    """
    Takes in the voice in text form and sends it to LLM and returns the converted drone command.
    """
    commands = {
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "forward": "Forward",
        "back": "Back"
    }
    command = text.lower()
    # Call the LLM to convert text
    result = run_terminal_agent(text)
    print(result)


def main():
    """
    The main function that runs the voice control program.
    """

    config = init.init()

    audio_processor = audio.AudioRecogniser()

    if config.voice_control.use_existing_recording:
        user_audio = audio_processor.load_audio()
    else:
        user_audio = audio_processor.capture_voice_input()

    text = audio_processor.convert_voice_to_text(user_audio)
    end_program = process_voice_command(text)

    root_logger(end_program)


if __name__ == "__main__":
    main()
