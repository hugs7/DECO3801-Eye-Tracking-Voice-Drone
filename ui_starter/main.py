from ui_setup import UISetup
from tkinter import *
import cv2
from PIL import Image, ImageTk
from typing import Optional


def main(app=None):
    """
    Defines entry point for the eye tracking application
    """
    if not app:
        app = Tk()
    ui_setup = UISetup(app)
    ui_setup.display_app()


if __name__ == "__main__":
    main()

