"""
Main module for the voice control program.
"""

import init
from LLM import run_terminal_agent
import logger_helper
import audio

root_logger = logger_helper.init_root_logger()


def process_voice_command(text: str):
    """
    Takes in the voice in text form and sends it to LLM and returns the converted drone command.

    Args:
        text: The voice command in text form.

    Returns:
        None
    """
    # Call the LLM to convert text
    result = run_terminal_agent(text)
    root_logger.info(result)


def main():
    """
    The main function that runs the voice control program.

    Returns:
        None
    """

    config = init.init()

    audio_processor = audio.AudioRecogniser()

    if config.voice_control.use_existing_recording:
        user_audio = audio_processor.load_audio()
    else:
        user_audio = audio_processor.capture_voice_input()

    text = audio_processor.convert_voice_to_text(user_audio)
    process_voice_command(text)

    root_logger.info("Done.")


if __name__ == "__main__":
    main()
