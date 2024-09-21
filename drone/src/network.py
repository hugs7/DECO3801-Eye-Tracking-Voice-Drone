"""
Network module
"""

import sys
import subprocess

from common.logger_helper import init_logger


logger = init_logger()


def connect_to_wifi(ssid: str, password: str) -> bool:
    """
    Connects to the specified wifi network

    Args:
        ssid (str): The SSID of the network to connect to
        password (str): The password of the network to connect to

    Returns:
        bool: True if connection was successful, False otherwise
    """
    logger.info("Connecting to wifi network '%s'...", ssid)

    if sys.platform == "win32":
        connect_cmd = f"netsh wlan connect name={ssid} ssid={ssid} key={password}"
    elif sys.platform == "linux":
        connect_cmd = f"nmcli device wifi connect {ssid} password {password}"
    elif sys.platform == "darwin":
        connect_cmd = f"networksetup -setairportnetwork en0 {ssid} {password}"

    logger.debug("Running connection command: %s", connect_cmd)

    try:
        subprocess.run(connect_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to connect to wifi network '%s'. Details: %s", ssid, e)
        return False

    logger.info("Successfully connected to wifi network '%s'", ssid)
    return True
