"""
Controller for the drone, handles the input of a drone from voice, Gaze or manual input
"""

from typing import Union, Optional, Dict, List
from threading import Event, Lock
import sys
import time

from omegaconf import OmegaConf
import cv2

from common import constants as cc, keyboard
from common.logger_helper import init_logger
from common.omegaconf_helper import conf_key_from_value
from common.loop import run_loop_with_max_tickrate, fps_to_ms
from common.PeekableQueue import PeekableQueue

from . import constants as c
from .drone_actions import DroneActions
from .flight_statistics import FlightStatistics
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
                raise ValueError(
                    "All or none of stop_event, thread_data, data_lock must be provided.")

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
        self.connect_to_drone = self.config.connect_to_drone
        self.drone_connected = self.connect_to_drone and self.model and self.model.success

        if self.drone_connected:
            self.drone_video_fps = self.model.video_fps

        self.keyboard_bindings = self.config.keyboard_bindings

        self._init_stat_params()
        logger.info("Drone controller initialised.")

    def _init_stat_params(self) -> None:
        """
        Initialises the drone statistics parameters and times for the controller.
        """

        logger.info("Initialising drone statistics parameters...")
        self.drone_stat_times = dict()
        self.drone_stat_params = OmegaConf.to_container(
            self.config.drone_stat_params, resolve=True)

        for param, tick_rate in self.drone_stat_params.items():
            milliseconds = fps_to_ms(tick_rate)
            self.drone_stat_params[param] = milliseconds
            self.drone_stat_times[param] = time.perf_counter()

        logger.info("Drone statistics parameters initialised %s",
                    self.drone_stat_params)

    def _controller_loop(self, tick_rate: float) -> bool:
        """
        One interation of the controller loop.

        Args:
            tick_rate (float): The tick rate of the loop

        Returns:
            True if the loop should continue, False otherwise
        """

        logger.debug(">>> Begin drone loop")

        self._event_loop()

        if self.drone_connected:
            ok, frame = self.model.read_camera()
            if not ok:
                return False

            self._render_frame(frame, tick_rate)
            self._get_drone_statistics(tick_rate)

        self.thread_loop_handler(self.stop_event)
        logger.debug("<<< End drone loop")
        return True

    def run(self) -> None:
        """
        Runs the main loop for the controller. Runs gui if in standalone mode.
        """

        if self.running_in_thread:
            logger.debug(
                "Drone module running in thread mode. Local GUI disabled.")

            run_loop_with_max_tickrate(
                self.config.max_tick_rate, self._controller_loop)
        else:
            logger.debug("Importing PyQt6...")

            from PyQt6.QtWidgets import QApplication
            from .gui import DroneApp

            gui = QApplication(sys.argv)
            drone_window = DroneApp(self)
            drone_window.wrap_show()
            gui.exec()

    def _render_frame(self, frame: cv2.typing.MatLike, tick_rate: float) -> None:
        """
        Encodes the frame and sends it to the main GUI for rendering.
        Should only be called in thread mode.

        Args:
            frame (cv2.typing.MatLike): The frame to render.
            tick_rate (float): The tick rate of the loop.
        """

        if not self.running_in_thread:
            logger.warning(
                "Video feed polling should be disabled in main mode")
            return

        if frame is None:
            logger.debug("No frame returned from camera")
            return

        with self.data_lock:
            self.thread_data[cc.DRONE][cc.VIDEO_FRAME] = frame
            self.thread_data[cc.DRONE][cc.TICK_RATE] = tick_rate

    def _get_drone_statistics(self, tick_rate: float) -> None:
        """
        Gets the flight statistics from the drone and sends it to the main GUI for rendering.
            - pitch
            - roll
            - yaw
            - speed_x
            - speed_y
            - speed_z
            - acceleration_x
            - acceleration_y
            - cceleration_z
            - lowest_temperature
            - highest_temperature
            - temperature
            - height
            - distance_tof
            - barometer
            - flight_time
            - battery

        Args:
            tick_rate (float): The tick rate of the loop.
        """
        if not self.drone_connected:
            return

        now = time.perf_counter()
        stat_vals = dict()

        # Battery
        if now - self.drone_stat_times[FlightStatistics.BATTERY.value] > self.drone_stat_params[FlightStatistics.BATTERY.value]:
            logger.debug("Getting battery level...")
            self.model.battery_level = self.model.get_battery()
            logger.info("Drone battery: %d", self.model.battery_level)
            self.drone_stat_times[FlightStatistics.BATTERY.value] = now

        stat_vals[FlightStatistics.BATTERY.value] = self.model.battery_level

        for statistic in FlightStatistics:
            statistic_value = statistic.value
            try:
                value = eval(f"self.model.drone.get_{statistic_value}()")
            except AttributeError:
                logger.warning(
                    "Method get_%s not found in drone model", statistic_value)
                continue

            logger.trace("Drone %s: %s", statistic_value, value)

        with self.data_lock:
            self.thread_data[cc.DRONE][cc.FLIGHT_STATISTICS] = stat_vals

    def _event_loop(self) -> None:
        """
        Wraps all event handling for the drone controller.
        """
        if not self.running_in_thread:
            return

        self._wait_key()
        self._wait_voice_command()

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

        if cc.KEYBOARD_QUEUE not in self.thread_data.keys():
            logger.trace("Keyboard queue not yet initialised in shared data.")
            return False

        keyboard_queue: PeekableQueue = self.thread_data[cc.KEYBOARD_QUEUE]
        key_buffer = keyboard.keyboard_event_loop(
            self.data_lock, keyboard_queue, self.keyboard_bindings)
        if not self.drone_connected:
            return

        accepted_keys = []
        for key_code in key_buffer:
            accepted_keys.append(self._handle_key_event(key_code))

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
            if self.model.in_flight:
                self.model.land()

            return True

        key_action = conf_key_from_value(
            self.keyboard_bindings, key_code, key_chr)
        if key_action is None:
            logger.trace("Key %s not found in keybindings", key_chr)
            return False

        key_recognised = key_action in {
            action.value for action in DroneActions}
        if key_recognised:
            self.perform_action(key_action)
        else:
            logger.warning(
                "Key action %s not found in DroneActions", key_action)

        return key_recognised

    def _wait_voice_command(self) -> bool:
        """
        Handles voice commands. If the voice command is recognised, it will be performed.

        Returns:
            True if a recognised voice command is received, False otherwise.
        """

        if not self.running_in_thread:
            logger.warning(
                "_wait_voice_command should not be called in main mode")
            return False

        if cc.DRONE not in self.thread_data.keys():
            logger.trace("Drone not yet initialised in shared data.")
            return False

        command_buffer: List[List] = []
        with self.data_lock:
            drone_data: Optional[Dict] = self.thread_data[cc.DRONE]
            if cc.COMMAND_QUEUE not in drone_data:
                logger.trace(
                    "Command queue not yet initialised in shared data.")
                return False

            command_queue: PeekableQueue = drone_data[cc.COMMAND_QUEUE]
            while not command_queue.empty():
                voice_command = command_queue.get()
                command_buffer.append(voice_command)

        accepted_commands = []
        if not self.drone_connected:
            return

        for voice_command in command_buffer:
            for command, measurement in voice_command:
                logger.info("Received voice command: %s", voice_command)
                accepted_commands.append(
                    self.perform_action(command, measurement))

        # Accept if any valid command was received
        return any(accepted_commands)

    def perform_action(self, command: str, measurement: Optional[int] = None) -> bool:
        """
        Handler for sending an action to the drone given a command.

        Args:
            command (str): The command to send to the drone. Can be any of the
                            commands defined in DroneActions.
            measurement (Optional[int]): The measurement to send with the command.
                                         Default is None.

        Returns:
            accepted (bool): True if the command was accepted, False otherwise.
        """

        command = command.lower()

        angle = 35
        dist = 20

        angle = measurement or angle
        dist = measurement or dist

        magnitude = None
        if command in c.DRONE_MOVEMENT_ACTIONS:
            magnitude = dist
        elif command in c.DRONE_ROTATION_ACTIONS:
            magnitude = angle
        else:
            logger.info("Performing action: %s", command)

        if magnitude is not None:
            logger.info("Performing action: %s with magnitude %d",
                        command, magnitude)

        try:
            match command:
                case DroneActions.ROTATE_CW:
                    self.model.rotate_clockwise(angle)
                case DroneActions.ROTATE_CCW:
                    self.model.rotate_counter_clockwise(angle)
                case DroneActions.UP:
                    self.model.move_up(dist)
                case DroneActions.DOWN:
                    self.model.move_down(dist)
                case DroneActions.LEFT:
                    self.model.move_left(dist)
                case DroneActions.RIGHT:
                    self.model.move_right(dist)
                case DroneActions.FORWARD:
                    self.model.move_forward(dist)
                case DroneActions.BACKWARD:
                    self.model.move_backward(dist)
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
                    return False
        except Exception as e:
            logger.error("Error sending command %s: %s", command, e)
            return False

        return True
