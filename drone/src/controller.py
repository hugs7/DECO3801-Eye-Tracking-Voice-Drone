"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union, Optional, Dict
from threading import Event, Lock

from omegaconf import OmegaConf

from common.logger_helper import init_logger
from common import constants as cc
from common.omegaconf_helper import conf_key_from_value

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
        drone: Union[TelloDrone, MavicDrone],
        controller_config: OmegaConf,
        stop_event: Optional[Event] = None,
        thread_data: Optional[Dict] = None,
        data_lock: Optional[Lock] = None,
    ):
        """
        Initialises the drone controller

        Args:
            drone [Union[TelloDrone, MavicDrone]]: The drone to control.
            controller_config [OmegaConf]: The configuration for the controller.
            stop_event: Event object to stop the gaze detector
            thread_data: Shared data dictionary
            data_lock: Lock object for shared data
        """

        logger.info("Initialising drone controller...")

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
        self.drone_video_fps = self.model.video_fps

        self.config = controller_config

        required_args = [stop_event, thread_data, data_lock]
        self.running_in_thread = any(required_args)

        logger.info("Drone controller initialised.")

    def handle_key_press(self, key_code: int) -> None:
        """
        Handles key press events for the drone controller.

        Args:
            key_code (int): The key code of the pressed key.

        Returns:
            None
        """

        key_chr = chr(key_code).lower()
        logger.info("Received key: %s (%d)", key_chr, key_code)

        if key_chr in cc.QUIT_KEYS:
            if self.drone.in_flight:
                self.model.land()

            return

        keybindings = self.config.keyboard_bindings
        key_action = conf_key_from_value(keybindings, key_code, key_chr)
        if key_action is None:
            logger.trace("Key %s not found in keybindings", key_chr)
            return

        if key_action in vars(DroneActions).values():
            self.perform_action(key_action)
        else:
            logger.warning("Key action %s not found in DroneActions", key_action)

    def perform_action(self, command: str):
        """
        Handler for sending an action to the drone given a command.

        Args:
            command (str): The command to send to the drone.
        command - String involving either up, down, left, right, forward, backward,
            cw(rotate clockwise), ccw (rotate counter clockwise)
        value - an int of the amount to change the drones direction by, if command is rotational
            use degrees and if a directional value use cm in direction
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
