"""
Controller for voice processing
"""

from typing import Optional, Tuple, List, Dict, Union
import ast
from multiprocessing import Queue as MPQueue

from omegaconf import OmegaConf

from common import constants as cc
from common.logger_helper import init_logger
from common.omegaconf_helper import conf_key_from_value

from . import constants as c
from .audio import AudioRecogniser
from .voice_actions import VoiceActions
from .LLM import LLM

logger = init_logger()


class VoiceController:
    """
    Controller for drone voice command module.
    """

    def __init__(self, config: OmegaConf, interprocess_data: Optional[Dict] = None):
        """
        Initialises the voice controller.

        Args:
            config (OmegaConf): Configuration for the voice controller.
            interprocess_data (Optional[Dict]): Interprocess communication (IPC) data dictionary:
                                           (Only provided if running as a child process)

        Returns:
            None
        """

        self.config = config
        self.voice_control_config = config.voice_control
        self.running_in_process = interprocess_data is not None
        self.loop_toggle = True

        if self.running_in_process:
            logger.info("Running in process mode")
            self.interprocess_data = interprocess_data
        else:
            logger.info("Running in main mode")

        self.audio_recogniser = AudioRecogniser(config.audio)
        self.llm = LLM(config.llm)

        self.keybindings = self.voice_control_config.keyboard_bindings

    def run(self) -> None:
        """
        Runs the voice processor.

        Returns:
            None
        """

        if self.voice_control_config.use_existing_recording:
            # For testing. Runs the audio once and then exits.
            user_audio = self.audio_recogniser.load_audio()
            self.process_voice_command(user_audio)
        else:
            run = True
            try:
                while run:
                    self._wait_key()

                    if self.loop_toggle:
                        if not self.audio_recogniser.network_available:
                            logger.error(
                                "No network available. Disabling loop.")
                            self.loop_toggle = False

                        if not self.audio_recogniser.microphone_available:
                            logger.error(
                                "No microphone available. Disabling loop.")
                            self.loop_toggle = False

                    if self.loop_toggle:
                        logger.info(" >>> Begin voice control loop")
                        run = self.audio_loop()
                        logger.info(" <<< End voice control loop")

            except KeyboardInterrupt:
                logger.error(
                    "    >>> Keyboard interrupt received. Exiting immediately.")
                run = False

    def _wait_key(self) -> None:
        if not self.running_in_process:
            return

        try:
            keyboard_queue: Optional[MPQueue] = self.interprocess_data[cc.KEYBOARD_QUEUE]
        except FileNotFoundError:
            logger.warning("Keyboard queue not found in shared data.")
            return
        except AttributeError:
            logger.warning("Keyboard queue not initialised in shared data.")
            return

        if keyboard_queue is not None:
            while not keyboard_queue.empty():
                key: int = keyboard_queue.get()
                self._keyboard_controller(key)
        else:
            logger.warning("Keyboard queue not initialised in shared data.")

    def _keyboard_controller(self, key_code: int) -> None:
        """
        Controller for keyboard input.

        Args:
            key_code (int): The key code received from the keyboard.
        """
        if not (0 <= key_code <= 0x110000):
            logger.warning("Keycode %d outside accepted range.", key_code)
            return

        key_chr = chr(key_code).lower()
        logger.info("Received key: %s (%d)", key_chr, key_code)

        key_action = conf_key_from_value(self.keybindings, key_code, key_chr)
        if key_action is None:
            logger.trace("Key %s not found in keybindings", key_chr)
            return False

        key_recognised = key_action in vars(VoiceActions).values()
        if key_recognised:
            self.perform_action(key_action)

    def perform_action(self, key_action: str) -> None:
        """
        Performs the action associated with the key action.

        Args:
            key_action (str): The action to perform.
        """
        match key_action:
            case VoiceActions.LOOP_TOGGLE:
                self.toggle_loop()

    def toggle_loop(self) -> None:
        """
        Toggles the loop on and off.
        """

        logger.info("Toggling loop to %s", self.loop_toggle)

        self.loop_toggle = not self.loop_toggle
        if self.loop_toggle:
            self.audio_recogniser.check_network_connection()

    def audio_loop(self) -> bool:
        """
        The main loop for the voice control program. Captures the user's voice and processes it.
        Depending upon config, either uses the microphone or the keyboard for input.

        Returns:
            bool: True if the loop should continue, False otherwise.
        """

        if self.voice_control_config.detect_voice:
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
        if self.voice_control_config.send_to_llm:
            parsed_command = self.process_voice_command(text)

        command_data[cc.PARSED_COMMAND] = parsed_command

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
        logger.info("Voice command: '%s'", user_command)
        logger.trace("Voice command of type %s", type(user_command))

        if result is None:
            logger.debug("No voice command detected.")
            return None

        # Parse the result into a list of tuples
        parsed_commands = None
        try:
            parsed_commands = ast.literal_eval(result)
        except Exception:
            logger.error("Failed to parse result into dictionary.")

        logger.info("Parsed voice command: '%s'", parsed_commands)
        logger.trace("Parsed voice command of type %s", type(parsed_commands))

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
            logger.trace(
                "Not running in process mode. Not saving command to shared data.")
            return

        command_text = command_data[cc.COMMAND_TEXT]
        logger.info("Setting voice command to '%s'", command_text)
        command_queue: MPQueue = self.interprocess_data[cc.VOICE_CONTROL][cc.COMMAND_QUEUE]
        command_queue.put(command_data)
        logger.debug(
            "Voice command added to command queue of length %d.", command_queue.qsize())
