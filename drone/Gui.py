import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

class DroneApp:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.root.title("Drone App")

        self.canvas = Canvas(self._root, width = 640, height = 480)
        self.canvas.pack(expand=True)

        self.update_video_feed()

        self.root.bind('<KeyPress>', self.on_key_press)

    def on_key_press(self, event):
        self.handle_keyboard_input(event.keysym)
    
    def handle_keyboard_input(self, command):
        key_mapping = {
        "Left": "LEFT",
        "Right": "RIGHT",
        "Up": "UP",
        "Down": "DOWN",
        "w": "FORWARD",
        "s": "BACKWARD",
        "l": "LAND",
        "space": "TAKEOFF",
        "q": "ROTATE CW",
        "e": "ROTATE CCW",
        "z": "FLIP FORWARD",
        }
        if command in key_mapping:
            self.controller.handle_input(key_mapping[command])

    def update_video_feed(self):
        frame = self.controller.get_frame()
        
        # Convert the image from OpenCV format to PIL format
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.canvas.image = image  # Keep a reference to avoid garbage collection
        self.root.after(20, self.update_video_feed)  # 50 FPS

        
        
    