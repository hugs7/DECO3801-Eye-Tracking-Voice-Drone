from ui_design import UIDesign
from tkinter import *
import cv2
from PIL import Image, ImageTk

class UISetup():
    def __init__(self, app: Tk) -> None:
        self._app = app
        self._canvas = Canvas(app, width=200, height=150)
        self._canvas.pack()
        self._design = UIDesign(self._canvas)

        self.initialise_key_presses(self._app)

        self._test_camera = self.set_test_camera()
        self._label_widget = Label(app) 
        self._label_widget.pack() 

    def set_test_camera(self) -> cv2.VideoCapture:
        """
        Sets the video capture object (used only for testing purposes)
        """
        vid = cv2.VideoCapture(0)
        width, height = 800, 600
        vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        return vid

    def open_camera(self): 
    
        # Capture the video frame by frame 
        _, frame = self._test_camera.read() 
    
        # Convert image from one color space to other 
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
    
        # Capture the latest frame and transform to image 
        captured_image = Image.fromarray(opencv_image) 
    
        # Convert captured image to photoimage 
        photo_image = ImageTk.PhotoImage(image=captured_image) 
    
        # Displaying photoimage in the label 
        self._label_widget.photo_image = photo_image 
    
        # Configure image in the label 
        self._label_widget.configure(image=photo_image) 
    
        # Repeat the same process after every 10 seconds 
        self._label_widget.after(10, self.open_camera) 

    def initialise_key_presses(self, app: Tk):

        app.bind('<o>', self._design.toggle_options_menu)
        self._design._options_displayed = not self._design._options_displayed

        app.bind('')

    def display_app(self):
        self.open_camera() ##Comment this out for integration

        self._app.mainloop()
