"""
Mavic Connect
"""

from dronekit import connect, VehicleMode


def mavic_connect():
    ip = "192.168.69.244"
    port = 14551

    connection_string = f"udp:{ip}:{port}"
    print(f"Connecting to mavic on: {connection_string}")

    # Try connecting with a longer timeout
    try:
        vehicle = connect(connection_string, wait_ready=True, timeout=60)
        print("Connected to vehicle!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        exit(1)

    return vehicle
