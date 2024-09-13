from tkinter import *
import cv2
from PIL import Image, ImageTk

class UIDesign():
    def __init__(self, canvas: Canvas) -> None:
        self._canvas = canvas
        self._options_displayed = False
        self._options_text = None

    def toggle_options_menu(self):
        if (self._options_displayed == True):
            self._options_text = self._canvas.create_text(300, 50, text="HELLO WORLD", fill="black", font=('Helvetica 15 bold'))
            self._canvas.pack()
        elif (self._options_displayed == False):
            self._canvas.delete(self._options_text)

