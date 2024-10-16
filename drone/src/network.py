"""
Network module
"""

from typing import Optional
import sys
import subprocess
import re
import os
import time

if __name__ == "__main__":

    # Add project directory to path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.insert(0, project_root)

from common.logger_helper import init_logger


logger = init_logger("DEBUG")


def win_ssid_profile_exists(ssid: str) -> bool:
    """
    Checks if a Wi-Fi profile exists on Windows.

    Args:
        ssid (str): The SSID to check for

    Returns:
        bool: True if the profile exists, False otherwise
    """
    result = subprocess.run(["netsh", "wlan", "show", "profile"], capture_output=True, text=True, shell=True)
    return ssid in result.stdout


def win_create_wifi_profile(ssid: str, password: str) -> None:
    """
    Create a Wi-Fi profile on Windows using an XML file.

    Args:
        ssid (str): The SSID of the network to connect to
        password (str): The password of the network to connect to. If the
                        network is open, pass an empty string

    Returns:
        None
    """
    shared_key = f"""
        <sharedKey>
            <keyType>passPhrase</keyType>
            <protected>false</protected>
            <keyMaterial>{password}</keyMaterial>
        </sharedKey>"""

    profile_content = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>{ 'WPA2PSK' if password else 'open' }</authentication>
                <encryption>{ 'AES' if password else 'none' }</encryption>
                <useOneX>false</useOneX>
            </authEncryption>{shared_key if password else ''}
        </security>
    </MSM>
</WLANProfile>
"""

    profile_file = f"{ssid}_profile.xml"
    with open(profile_file, "w") as f:
        f.write(profile_content)

    subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_file}"], shell=True)

    os.remove(profile_file)


def is_wifi_connected() -> bool:
    """
    Checks if the device is connected to a Wi-Fi network

    Returns:
        bool: True if connected, False otherwise
    """
    if sys.platform == "win32":
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, shell=True)
        pattern = r"State\s+:\s+connected"
        return re.search(pattern, result.stdout, re.MULTILINE) is not None
    elif sys.platform == "linux":
        result = subprocess.run(["iwgetid"], capture_output=True, text=True, shell=True)
        return "ESSID" in result.stdout
    elif sys.platform == "darwin":
        result = subprocess.run(["networksetup", "-getairportnetwork", "en0"], capture_output=True, text=True, shell=True)
        return "Current Wi-Fi Network" in result.stdout


def refresh_networks() -> None:
    """
    Refreshes the list of available Wi-Fi networks
    """

    logger.info("Refreshing available networks...")
    if sys.platform == "win32":
        subprocess.run("explorer.exe ms-availablenetworks:", capture_output=False)
    elif sys.platform == "linux":
        subprocess.run(["nmcli", "device", "wifi", "rescan"], capture_output=False)
    elif sys.platform == "darwin":
        subprocess.run(["networksetup", "-detectnewhardware"], capture_output=False)

    time.sleep(3)


def connect_to_wifi(ssid: str, password: str, network_interface: Optional[str] = None, max_attempts: int = 3, delay: float = 5.0) -> bool:
    """
    Connects to the specified wifi network

    Args:
        ssid (str): The SSID of the network to connect to
        password (str): The password of the network to connect to. If the
                        network is open, pass an empty string
        network_interface (Optional[str], optional): The network interface to connect from.
                                                     Only required for MacOS. Defaults to None.
        max_attempts (int, optional): The maximum number of attempts to connect. Defaults to 3.
        delay (float, optional): Delay when checking WiFi Connection

    Returns:
        bool: True if connection was successful, False otherwise
    """
    logger.info("Connecting to wifi network '%s'...", ssid)
    refresh_networks()

    if sys.platform == "win32":
        if win_ssid_profile_exists(ssid):
            logger.info("Wi-Fi profile for network '%s' already exists", ssid)
        else:
            logger.info("Creating Wi-Fi profile for network '%s'", ssid)
            win_create_wifi_profile(ssid, password)

        connect_cmd = f'netsh wlan connect name="{ssid}"'
    elif sys.platform == "linux":
        connect_cmd = f'nmcli device wifi connect "{ssid}"'
        if password:
            connect_cmd += f' password "{password}"'
    elif sys.platform == "darwin":
        if not network_interface:
            network_interface = "en0"

        connect_cmd = f'networksetup -setairportnetwork {network_interface} "{ssid}"'
        if password:
            connect_cmd += f' "{password}"'

    logger.debug("Running connection command: %s for a maximum of %d connection attempts", connect_cmd, max_attempts)

    connected = False
    attempts = 0

    while not connected and attempts < max_attempts:
        try:
            subprocess.run(connect_cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            attempts += 1
            continue

        time.sleep(delay)
        connected = is_wifi_connected()
        if connected:
            logger.info("Successfully connected to wifi network '%s' on attempt %d", ssid, attempts)
        else:
            logger.error("Failed to connect to wifi network '%s'", ssid)

        attempts += 1

    return connected


if __name__ == "__main__":
    # TESTING ONLY. DO NOT COMMIT YOUR SSID AND PASSWORD
    placeholder = "___"

    ssid = placeholder
    password = placeholder

    if ssid == placeholder or password == placeholder:
        logger.error("Please provide a valid SSID and password for testing")
        sys.exit(1)
    connect_to_wifi(ssid, password)
