"""
Defines class for Tello drone
"""

from djitellopy import tello
import cv2
from omegaconf import OmegaConf

from common.logger_helper import init_logger

from .drone import Drone
from .. import constants as c

logger = init_logger()


class TelloDrone(Drone):
    """
    Implements a Tello drone wrapper class
    """

    def __init__(self, tello_config: OmegaConf) -> None:
        """
        Initialises the Tello drone

        Args:
            tello_config (OmegaConf): The Tello config object
        """

        logger.info("Initialising TelloDrone...")
        self.config = tello_config

        tello_drone = tello.Tello()
        self.drone = tello_drone
        self.connect()
        self.polling_flag = False

        # Start Camera Display Stream
        self.drone.streamon()
        self.drone.set_speed(c.TELLO_SPEED_CM_S)

        logger.info("Drone battery: %d", self.drone.get_battery())

    def connect(self) -> None:
        """
        Connects to the drone
        """

        logger.info("Connecting to the Tello Drone...")

        try:
            self.drone.connect()
        except tello.TelloException as e:
            logger.error("There was an issue connecting to the drone. Check you are on the correct WiFi network.")
            logger.error("Details %s", e)

        logger.info("Connected to the Tello Drone")

    def read_camera(self) -> cv2.typing.MatLike:
        """
        Reads the camera feed from the drone

        Returns:
            img - the image from the camera feed
        """

        frame_read = self.drone.get_frame_read()
        img = frame_read.frame

        return img

    def set_video_resolution(self, resolution: str):
        """Sets the resolution of the video stream
        Use one of the following for the resolution argument:
            Tello.RESOLUTION_480P
            Tello.RESOLUTION_720P
        """
        cmd = "setresolution {}".format(resolution)
        self.drone.send_control_command(cmd)

    def set_video_fps(self, fps: str):
        """Sets the frames per second of the video stream
        Use one of the following for the fps argument:
            Tello.FPS_5
            Tello.FPS_15
            Tello.FPS_30
        """
        cmd = "setfps {}".format(fps)
        self.drone.send_control_command(cmd)

    def set_video_bitrate(self, bitrate: int):
        """Sets the bitrate of the video stream
        Use one of the following for the bitrate argument:
            Tello.BITRATE_AUTO
            Tello.BITRATE_1MBPS
            Tello.BITRATE_2MBPS
            Tello.BITRATE_3MBPS
            Tello.BITRATE_4MBPS
            Tello.BITRATE_5MBPS
        """
        cmd = "setbitrate {}".format(bitrate)
        self.drone.send_control_command(cmd)

    def send_info(self, command):
        if self.polling_flag:
            self.drone.send_control_command(command)
        else:
            self.drone.send_command_without_return(command)
        # data, address = client_socket.recvfrom(1024)
        # client_socket.sendto(command.encode('utf-8'), address)

    # Controlling methods
    '''def send_control_command(self, command: str, timeout: int = RESPONSE_TIMEOUT) -> bool:
        """Send control command to Tello and wait for its response.
        Internal method, you normally wouldn't call this yourself.
        """
        response = "max retries exceeded"
        for i in range(0, self.retry_count):
            response = self.send_command_without_return(command, timeout=timeout) #USUALLY SEND WITH RETURN

            if 'ok' in response.lower():
                return True

            self.LOGGER.debug("Command attempt #{} failed for command: '{}'".format(i, command))

        self.raise_result_error(command, response)
        return False # never reached
    '''

    # valid tello command strings:
    """
    Connect = "command"
    Takeoff = "takeoff", 20sec
    Land = "land"
    Stream on = "streamon"
    Stream off = "streamoff"
    Emergency off = "emergency"
    Movement = "direction magnitude"
    directions = {"up", "down", "left", "right", "forward", "back"}
    Rotate CW = "cw magnitude"
    Rotate CCW = "ccw magnitude"
    Flip = "flip direction"
    directions = {"l", "r", "f", "b"}
    """

    def rotate_clockwise(self, degrees: int) -> None:
        command = "cw {}".format(degrees)
        self.send_info(command)

    def rotate_counter_clockwise(self, degrees: int) -> None:
        command = "ccw {}".format(degrees)
        self.send_info(command)

    def move_up(self, cm: int) -> None:
        command = "up {}".format(cm)
        self.send_info(command)

    def move_down(self, cm: int) -> None:
        command = "down {}".format(cm)
        self.send_info(command)

    def move_left(self, cm: int) -> None:
        command = "left {}".format(cm)
        self.send_info(command)

    def move_right(self, cm: int) -> None:
        command = "right {}".format(cm)
        self.send_info(command)

    def move_forward(self, cm: int) -> None:
        command = "forward {}".format(cm)
        self.send_info(command)

    def move_backward(self, cm: int) -> None:
        command = "back {}".format(cm)
        self.send_info(command)

    def takeoff(self) -> None:
        command = "takeoff"
        self.send_info(command)

    def land(self) -> None:
        command = "land"
        self.send_info(command)

    def flip_forward(self) -> None:
        command = "flip f"
        self.send_info(command)

    # Polling methods
    def get_altitude(self) -> int:
        """
        Gets the altitude of the drone
        :return: The altitude of the drone
        """
        pass
