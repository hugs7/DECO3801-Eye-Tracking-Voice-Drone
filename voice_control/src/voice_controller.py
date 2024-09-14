"""
Controller for voice processing
"""

from typing import Optional, Tuple, List
from threading import Event, Lock
import ast
from omegaconf import OmegaConf

import speech_recognition as sr

from common.logger_helper import init_logger

from .audio import AudioRecogniser
from .LLM import run_terminal_agent

logger = init_logger()


class VoiceController:
    def __init__(
        self, config, stop_event: Optional[Event] = None, shared_data: Optional[OmegaConf] = None, data_lock: Optional[Lock] = None
    ):
        """
        Initialises the voice controller.

        Args:
            config: The configuration object

            (Only provided if running as a child thread)
            stop_event: Event to signal stop
            shared_data: Shared data between threads
            data_lock: Lock for shared data

        Returns:
            None
        """

        self.config = config

        self.recogniser = sr.Recognizer()
        self.audio_recogniser = AudioRecogniser(config.audio)

        required_args = [stop_event, shared_data, data_lock]
        self.running_in_thread = any(required_args)

        if self.running_in_thread:
            # If running in thread mode, all or none of the required args must be provided
            if not all(required_args):
                raise ValueError("All or none of stop_event, shared_data, data_lock must be provided.")

            logger.info("Running in thread mode")
            self.stop_event = stop_event
            self.shared_data = shared_data
            self.data_lock = data_lock

            # Lazily import thread helpers only if running in thread mode
            from app.thread_helper import thread_loop_handler

            # Bind to class attributes so we can access later in class methods
            self.thread_loop_handler = thread_loop_handler
        else:
            logger.info("Running in main mode")

    def run(self) -> None:
        """
        Runs the voice processor.

        Returns:
            None
        """

        if self.config.voice_control.use_existing_recording:
            # For testing. Runs the audio once and then exits.
            user_audio = self.audio_recogniser.load_audio()
            self.process_voice_command(user_audio)
        else:
            run = True
            while run:
                logger.info(" >>> Begin voice control loop")
                run = self.audio_loop()

                if self.running_in_thread:
                    self.thread_loop_handler(self.stop_event)

                logger.info(" <<< End voice control loop")

    def audio_loop(self) -> bool:
        """
        The main loop for the voice control program. Captures the user's voice and processes it.
        Depending upon config, either uses the microphone or the keyboard for input.

        Returns:
            bool: True if the loop should continue, False otherwise.
        """

        if self.config.voice_control.detect_voice:
            user_audio = self.audio_recogniser.capture_voice_input()
            text = self.audio_recogniser.convert_voice_to_text(user_audio)
        else:
            text = input("Enter command: ")

        if self.config.voice_control.send_to_llm:
            self.process_voice_command(text)

        return True  # For now

    def process_voice_command(self, user_command: str) -> Optional[List[Tuple[str, int]]]:
        """
        Takes in the voice in text form and sends it to LLM and returns the converted drone command.
        If running in thread mode, the result is stored in shared_data to send to the drone controller.
        If the command cannot be parsed, returns (and if applicable sets the shared data to) None.

        Args:
            user_command (str): The voice command in text form.

        Returns:
            Optional[list[tuple[str, int]]]: The drone command as a dictionary of the form
                                             [()"command": int), ...] or None if the command
                                             is invalid.
        """
        result = run_terminal_agent(user_command)
        logger.info(f"Result: '{result}' of type {type(result)}")

        # Parse the result into a list of tuples
        parsed_commands = None
        try:
            parsed_commands = ast.literal_eval(result)
        except Exception:
            logger.error("Failed to parse result into dictionary.")

        logger.info(f"Voice command: {parsed_commands} of type {type(parsed_commands)}")

        if self.running_in_thread:
            logger.info(f"Setting voice command to {parsed_commands}")
            with self.data_lock:
                self.shared_data.voice_control.voice_command = parsed_commands

            logger.debug("Voice command set in shared data.")

        return parsed_commands
