"""
Controller for voice processing
"""

from typing import Optional, Tuple, List, Dict, Union
import ast

from omegaconf import OmegaConf

from common import constants as cc
from common.logger_helper import init_logger
from common.PeekableMPQueue import PeekableMPQueue

from .audio import AudioRecogniser
from .LLM import LLM

logger = init_logger()


class VoiceController:
    def __init__(self, config: OmegaConf, manager_data: Optional[Dict] = None):
        """
        Initialises the voice controller.

        Args:
            config (OmegaConf): Configuration for the voice controller.
            manager_data (Optional[Dict]): Interprocess communication (IPC) data dictionary:
                                           (Only provided if running as a child process)

        Returns:
            None
        """

        self.config = config

        self.running_in_process = manager_data is not None
        if self.running_in_process:
            logger.info("Running in process mode")
            self.manager_data = manager_data
        else:
            logger.info("Running in main mode")

        self.audio_recogniser = AudioRecogniser(config.audio)
        self.llm = LLM(config.llm)

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
            try:
                while run:
                    logger.info(" >>> Begin voice control loop")
                    run = self.audio_loop()

                    logger.info(" <<< End voice control loop")
            except KeyboardInterrupt:
                logger.error("    >>> Keyboard interrupt received. Exiting immediately.")
                run = False

    def audio_loop(self) -> bool:
        """
        The main loop for the voice control program. Captures the user's voice and processes it.
        Depending upon config, either uses the microphone or the keyboard for input.

        Returns:
            bool: True if the loop should continue, False otherwise.
        """

        if self.config.voice_control.detect_voice:
            if not self.audio_recogniser.microphone_available:
                return False

            user_audio = self.audio_recogniser.capture_voice_input()
            if user_audio is None:
                # Keep the loop running
                return True

            text = self.audio_recogniser.convert_voice_to_text(user_audio)
        else:
            text = input("Enter command: ")

        command_data = {cc.COMMAND_TEXT: text}

        parsed_command = None
        if self.config.voice_control.send_to_llm:
            parsed_command = self.process_voice_command(text)

        command_data["parsed_command"] = parsed_command

        self.save_command_to_thread_data(command_data)

        return True

    def process_voice_command(self, user_command: str) -> Optional[List[Tuple[str, int]]]:
        """
        Takes in the voice in text form and sends it to LLM and returns the converted drone command.
        If running in thread mode, the result is stored in thread_data to send to the drone controller.
        If the command cannot be parsed, returns (and if applicable sets the shared data to) None.

        Args:
            user_command (str): The voice command in text form.

        Returns:
            Optional[list[tuple[str, int]]]: The drone command as a dictionary of the form
                                             [()"command": int), ...] or None if the command
                                             is invalid.
        """
        result = self.llm.run_terminal_agent(user_command)
        logger.info(f"Voice command: '%s'", user_command)
        logger.trace(f"Voice command of type %s", type(user_command))

        # Parse the result into a list of tuples
        parsed_commands = None
        try:
            parsed_commands = ast.literal_eval(result)
        except Exception:
            logger.error("Failed to parse result into dictionary.")

        logger.info(f"Parsed voice command: '%s'", parsed_commands)
        logger.trace(f"Parsed voice command of type %s", type(parsed_commands))
        self.save_command_to_thread_data(parsed_commands)

        return parsed_commands

    def save_command_to_thread_data(self, command_data: Dict[str, Union[str, List[Tuple[str, int]]]]) -> None:
        """
        Saves the command to the shared data.

        Args:
            command_data (Dict[str, Union[str, List[Tuple[str, int]]]]): The command to save.

        Returns:
            None
        """
        if not self.running_in_process:
            logger.trace("Not running in process mode. Not saving command to shared data.")
            return

        command_text = command_data[cc.COMMAND_TEXT]
        logger.info(f"Setting voice command to '%s'", command_text)
        command_queue: PeekableMPQueue = self.manager_data[cc.VOICE_CONTROL][cc.COMMAND_QUEUE]
        command_queue.put(command_data)
        logger.debug("Voice command added to command queue of length %d.", command_queue.qsize())
