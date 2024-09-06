"""
Main module of the Drone Project.
Hugo Burton
06/09/2024
"""

from threading import Thread, Event
import logging
from time import sleep

if __name__ == "__main__":
    from eye_tracking import main as eye_tracking_loop
    from voice_control import main as voice_control_loop
    from drone import main as drone_loop
else:
    from .eye_tracking import main as eye_tracking_loop
    from .voice_control import main as voice_control_loop
    from .drone import main as drone_loop

stop_event = Event()


def thread_wrapper(func) -> None:
    """
    Wrapper function to run a function in a thread.
    Passes a stop event to the function as a signal to stop execution.
    :param func: Function to run in a thread
    :return: None
    """
    while not stop_event.is_set():
        func(stop_event)


def is_any_thread_alive(threads):
    return any(t.is_alive() for t in threads)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(" >>> Begin")

    # Create threads for each of the components
    threads = [
        Thread(target=lambda: thread_wrapper(eye_tracking_loop)),
        Thread(target=lambda: thread_wrapper(voice_control_loop)),
        Thread(target=lambda: thread_wrapper(drone_loop)),
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    try:
        # Periodically check if any thread is alive
        while is_any_thread_alive(threads):
            # Sleep for a short duration to prevent busy-waiting
            sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Interrupted! Stopping all threads...")
        stop_event.set()  # Signal all threads to stop

        # Ensure all threads are properly joined after signaling them to stop
        for thread in threads:
            thread.join()

    logging.info(" <<< End")


if __name__ == "__main__":
    main()
