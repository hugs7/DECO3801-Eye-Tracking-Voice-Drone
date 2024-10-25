"""
Common network functions
"""


import socket


def check_internet_connection(host="www.google.com.au", port=80, timeout=5):
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
