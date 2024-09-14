"""
Main module for the voice control program.
"""

import logging

import init
from LLM import run_terminal_agent
import audio

logger = logging.getLogger(__name__)


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

    logger.info("Initialising voice control program.")
    config = init.init_config()

    audio_processor = audio.AudioRecogniser()

    user_audio = audio_processor.capture_voice_input()
    text = audio_processor.convert_voice_to_text(user_audio)
    end_program = process_voice_command(text)
    logger(end_program)


if __name__ == "__main__":
    main()
