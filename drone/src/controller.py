"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union, Optional, Dict, List
from threading import Event, Lock
from queue import Queue
from datetime import datetime
import sys
import time

from omegaconf import OmegaConf
import cv2

from common import constants as cc, keyboard
from common.logger_helper import init_logger
from common.omegaconf_helper import conf_key_from_value
from common.gui_helper import fps_to_ms

from .drone_actions import DroneActions
from .models.tello_drone import TelloDrone
from .models.mavic_drone import MavicDrone

logger = init_logger()


class Controller:
    """
    Controller for the drone, handles the input of a drone from voice, Gaze or manual input
    """

    def __init__(
        self,
        drone: Optional[Union[TelloDrone, MavicDrone]],
        controller_config: OmegaConf,
        stop_event: Optional[Event] = None,
        thread_data: Optional[Dict] = None,
        data_lock: Optional[Lock] = None,
    ):
        """
        Initialises the drone controller

        Args:
            drone Optional[Union[TelloDrone, MavicDrone]]: The drone to control or none
                                                        if running in limited mode.
            controller_config [OmegaConf]: The configuration for the controller.
            stop_event: Event object to stop the gaze detector
            thread_data: Shared data dictionary
            data_lock: Lock object for shared data
        """

        logger.info("Initialising drone controller...")

        required_args = [stop_event, thread_data, data_lock]
        self.running_in_thread = any(required_args)

        if self.running_in_thread:
            # If running in thread mode, all or none of the required args must be provided
            if not all(required_args):
                raise ValueError("All or none of stop_event, thread_data, data_lock must be provided.")

            logger.info("Running in thread mode")
            self.stop_event = stop_event
            self.thread_data = thread_data
            self.data_lock = data_lock

            logger.debug("Initialising thread helper functions")
            # Lazily import thread helpers only if running in thread mode
            from common.thread_helper import thread_loop_handler, thread_exit

            # Bind to class attributes so we can access them in class methods
            self.thread_loop_handler = thread_loop_handler
            self.thread_exit = thread_exit

            logger.debug("Thread initialisation complete")
        else:
            logger.info("Running in main mode")

        self.model = drone
        self.config = controller_config
        self.gui_only = self.config.gui_only
        self.min_loop_time = fps_to_ms(self.config.max_tick_rate)

        if not self.gui_only and self.model.success:
            self.drone_video_fps = self.model.video_fps

        logger.info("Drone controller initialised.")

    def run(self) -> None:
        """
        Runs the main loop for the controller. Runs gui if in standalone mode.
        """

        if self.running_in_thread:
            logger.debug("Drone module running in thread mode. Local GUI disabled.")

            last_loop_start_time = datetime.now()
            while True:
                logger.debug(">>> Begin drone loop")
                now = datetime.now()

                diff = now - last_loop_start_time
                if diff.total_seconds() * 1000 < self.min_loop_time:
                    time.sleep((self.min_loop_time - diff.total_seconds() * 1000) / 1000)

                last_loop_start_time = datetime.now()

                self._wait_key()

                if self.model.success:
                    ok, frame = self.model.read_camera()
                    if not ok:
                        break

                    self._render_frame(frame)

                self.thread_loop_handler(self.stop_event)
                logger.debug("<<< End drone loop")
        else:
            logger.debug("Importing PyQt6...")

            from PyQt6.QtWidgets import QApplication
            from .gui import DroneApp

            gui = QApplication(sys.argv)
            drone_window = DroneApp(self)
            drone_window.show()
            gui.exec()

    def _render_frame(self, frame: cv2.typing.MatLike) -> None:
        """
        Encodes the frame and sends it to the main GUI for rendering.
        Should only be called in thread mode.

        Args:
            frame (cv2.typing.MatLike): The frame to render.
        """

        if not self.running_in_thread:
            logger.warning("Video feed polling should be disabled in main mode")
            return

        if frame is None:
            logger.debug("No frame returned from camera")
            return

        with self.data_lock:
            self.thread_data["drone"]["video_frame"] = frame

    def _wait_key(self) -> bool:
        """
        Handles keyboard commands either from cv2 GUI if running as module or
        from GUI if running in thread mode. Will handle multiple keys if there is more
        than one in the queue.

        Returns:
            True if a recognised key is pressed (or any if there are multiple in the queue).
            False otherwise.
        """

        if not self.running_in_thread:
            logger.warning("_wait_key should not be called in main mode")
            return False

        # Define a buffer so that we are not locking the data for too long.
        # Not critical while keyboard inputs are simple, however, this is good
        # practice for more complex inputs.
        key_buffer: List[int] = []
        with self.data_lock:
            keyboard_queue: Optional[Queue] = self.thread_data["keyboard_queue"]
            if keyboard_queue is not None:
                while not keyboard_queue.empty():
                    key: int = keyboard_queue.get()
                    key_buffer.append(key)
            else:
                logger.warning("Keyboard queue not initialised in shared data.")

        accepted_keys = []
        for key in key_buffer:
            accepted_keys.append(self._handle_key_event(key))

        # Accept if any valid key was pressed
        return any(accepted_keys)

    def _handle_key_event(self, key_code: int) -> bool:
        """
        Handles key press events for the drone controller.

        Args:
            key_code (int): The key code of the pressed key.

        Returns:
            True if a recognised key is pressed, False otherwise
        """

        key_chr = keyboard.get_key_chr(key_code)

        logger.info("Received key: %s (%d)", key_chr, key_code)

        if key_chr in cc.QUIT_KEYS:
            if self.drone.in_flight:
                self.model.land()

            return True

        keybindings = self.config.keyboard_bindings
        key_action = conf_key_from_value(keybindings, key_code, key_chr)
        if key_action is None:
            logger.trace("Key %s not found in keybindings", key_chr)
            return False

        key_recognised = key_action in vars(DroneActions).values()
        if key_recognised:
            self.perform_action(key_action)
        else:
            logger.warning("Key action %s not found in DroneActions", key_action)

        return key_recognised

    def perform_action(self, command: str) -> None:
        """
        Handler for sending an action to the drone given a command.

        Args:
            command (str): The command to send to the drone.
            TODO: Add docstring for command format
        """

        try:
            match command:
                case DroneActions.ROTATE_CW:
                    self.model.rotate_clockwise(90)
                case DroneActions.ROTATE_CCW:
                    self.model.rotate_counter_clockwise(90)
                case DroneActions.UP:
                    self.model.move_up(50)
                case DroneActions.DOWN:
                    self.model.move_down(50)
                case DroneActions.LEFT:
                    self.model.move_left(50)
                case DroneActions.RIGHT:
                    self.model.move_right(50)
                case DroneActions.FORWARD:
                    self.model.move_forward(50)
                case DroneActions.BACKWARD:
                    self.model.move_backward(50)
                case DroneActions.TAKEOFF:
                    self.model.takeoff()
                case DroneActions.LAND:
                    self.model.land()
                case DroneActions.FLIP_FORWARD:
                    self.model.flip_forward()
                case DroneActions.EMERGENCY:
                    self.model.emergency()
                case DroneActions.MOTOR_ON:
                    self.model.motor_on()
                case DroneActions.MOTOR_OFF:
                    self.model.motor_off()
                case _:
                    logger.warning("Command %s not recognised", command)
        except Exception as e:
            logger.error("Error sending command %s: %s", command, e)
