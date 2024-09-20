"""
Local drone GUI. Not used in threading mode.
"""

import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

from .controller import Controller
from .utils import file_handler as fh


class DroneApp:
    """
    Local drone GUI
    """

    WIDTH = 640
    HEIGHT = 480

    def __init__(self, root, controller: Controller):
        """
        Initialises the drone app

        Args:
            root: The root window
            controller: The controller object
        """
        self.root = root
        self.controller = controller

        self.root.title("Drone App")

        self.canvas = Canvas(self.root, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack(expand=True)

        loading_screen_path = fh.get_assets_folder() / "loadingScreen.png"
        base_image = Image.open(loading_screen_path)
        base_image = base_image.resize((self.WIDTH, self.HEIGHT), Image.Resampling.BILINEAR)
        base_image = ImageTk.PhotoImage(base_image)

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=base_image)

        self.update_video_feed()

        self.root.bind("<KeyPress>", self.on_key_press)

    def on_key_press(self, event: tk.Event):
        """
        Handles key press events

        Args:
            event: The key press event
        """
        self.controller.handle_input(event.keysym)

    def update_video_feed(self):
        """
        Updates the video feed
        """
        frame = self.controller.model.get_frame()

        if frame is not None:
            # Convert the image from OpenCV format to PIL format
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)

            # Update image
            self.canvas.itemconfig(self.image_on_canvas, image=image)

            # Save image so it isn't garbage collected
            self.canvas.image = image

        self.root.after(30, self.update_video_feed)
