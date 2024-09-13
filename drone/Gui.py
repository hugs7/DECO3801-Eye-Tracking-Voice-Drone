import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

class DroneApp:
    WIDTH = 640
    HEIGHT = 480

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.root.title("Drone App")

        self.canvas = Canvas(self.root, width = self.WIDTH, height = self.HEIGHT)
        self.canvas.pack(expand=True)

        base_image = Image.open("./assets/loadingScreeen.png")
        base_image = base_image.resize((self.WIDTH, self.HEIGHT), Image.ANTIALIAS)  # Resize the image to fit the canvas
        base_image = ImageTk.PhotoImage(base_image)

        # Display the base image first
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=base_image)

        self.update_video_feed()

        self.root.bind('<KeyPress>', self.on_key_press)

    def on_key_press(self, event):
        self.controller.handle_keyboard_input(event.keysym)

    def parse_input(self, command):
        self.controller.handle_input(command)

    def update_video_feed(self):
        frame = self.controller.get_frame()

        if frame is not None:
            # Convert the image from OpenCV format to PIL format
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)

            # Update image
            self.canvas.itemconfig(self.image_on_canvas, image=image)

            # Save image so it isn't garbage collected
            self.canvas.image = image

        self.root.after(12, self.update_video_feed)  # 30 FPSish
    

        
        
    