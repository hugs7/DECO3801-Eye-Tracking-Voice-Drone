"""
Controller for voice processing
"""

from typing import Optional, Dict, List
from threading import Event, Lock
import json

import speech_recognition as sr

from logger_helper import init_logger
from audio import AudioRecogniser
from LLM import run_terminal_agent

logger = init_logger()


class VoiceController:
    def __init__(self, config, stop_event: Optional[Event] = None, shared_data: Optional[Dict] = None, data_lock: Optional[Lock] = None):
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
        self.audio_recogniser = AudioRecogniser()

        required_args = [stop_event, shared_data, data_lock]
        self.running_in_thread = any(required_args)

        if self.running_in_thread:
            # If running in thread mode, all or none of the required args must be provided
            if not all(required_args):
                raise ValueError(
                    "All or none of stop_event, shared_data, data_lock must be provided.")

            logger.info("Running in thread mode")
            self.stop_event = stop_event
            self.shared_data = shared_data
            self.data_lock = data_lock

            # Lazily import thread helpers only if running in thread mode
            from app.thread_helper import thread_exit_handler, is_main_thread

            # Bind to class attributes so we can access them in class methods
            self.thread_exit_handler = thread_exit_handler
            self.is_main_thread = is_main_thread
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
                    self.thread_exit_handler(self.stop_event)

                logger.info(" <<< End voice control loop")

    def audio_loop(self) -> bool:
        """
        The main loop for the voice control program. Captures the user's voice and processes it.

        Returns:
            bool: True if the loop should continue, False otherwise.
        """

        user_audio = self.audio_recogniser.capture_voice_input()

        text = self.audio_recogniser.convert_voice_to_text(user_audio)
        self.process_voice_command(text)

        return True  # For now

    def process_voice_command(self, user_audio: sr.AudioData) -> Optional[List[Dict[str, int]]]:
        """
        Takes in the voice in text form and sends it to LLM and returns the converted drone command.
        If running in thread mode, the result is stored in shared_data to send to the drone controller.
        If the command cannot be parsed, returns (and if applicable sets the shared data to) None.

        Args:
            user_audio {sr.AudioData}: The audio data from the user.

        Returns:
            Optional[list[dict[str, int]]]: The drone command as a dictionary of the form [{"command": int}] or None if the command is invalid.
        """
        text = self.audio_recogniser.convert_voice_to_text(user_audio)
        result = run_terminal_agent(text)
        logger.info(result)

        # Parse the result into a dictionary
        try:
            result_dict = json.loads(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse result into dictionary.")
            result_dict = None

        if self.running_in_thread:
            with self.data_lock:
                self.shared_data["voice_control"]["voice_command"] = result_dict

        return result_dict
