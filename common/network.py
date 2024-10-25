"""
Common network functions
"""


import socket

from .logger_helper import init_logger

logger = init_logger()


def check_internet_connection(host="www.google.com.au", port=80, timeout=5):
    """
    Check if the device is connected to the internet.

    Args:
        host (str, optional): The host to check for connection. Defaults to "www.google.com.au".
        port (int, optional): The port to check for connection. Defaults to 80.
        timeout (int, optional): The timeout for the connection check. Defaults to 5.

    Returns:
        bool: True if the device is connected to the internet, False otherwise.
    """

    logger.info("Checking internet connection at %s:%s", host, port)

    try:
        # Attempt to resolve the host to check for connection
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


if __name__ == "__main__":
    if check_internet_connection():
        print("Connected to the internet")
    else:
        print("No internet connection")
