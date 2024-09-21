"""
Network module
"""

from typing import Optional
import sys
import subprocess

from common.logger_helper import init_logger


logger = init_logger()


def connect_to_wifi(ssid: str, password: str, network_interface: Optional[str] = None) -> bool:
    """
    Connects to the specified wifi network

    Args:
        ssid (str): The SSID of the network to connect to
        password (str): The password of the network to connect to. If the
                        network is open, pass an empty string
        network_interface (Optional[str], optional): The network interface to connect from.
                                                     Only required for MacOS. Defaults to None.

    Returns:
        bool: True if connection was successful, False otherwise
    """
    logger.info("Connecting to wifi network '%s'...", ssid)

    if sys.platform == "win32":
        connect_cmd = f"netsh wlan connect name={ssid} ssid={ssid} key={password}"
    elif sys.platform == "linux":
        connect_cmd = f"nmcli device wifi connect {ssid} password {password}"
    elif sys.platform == "darwin":
        if not network_interface:
            network_interface = "en0"
        connect_cmd = f"networksetup -setairportnetwork {network_interface} {ssid} {password}"

    logger.debug("Running connection command: %s", connect_cmd)

    try:
        subprocess.run(connect_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to connect to wifi network '%s'. Details: %s", ssid, e)
        return False

    logger.info("Successfully connected to wifi network '%s'", ssid)
    return True
