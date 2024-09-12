from controller import Controller
from TelloModel import TelloModel
from Gui import DroneApp
import tkinter as tk


def init(drone_type):
    if drone_type == "mavic":
        pass
    else:
        return TelloModel()

def main():
    drone_type = "tello"
    drone = init(drone_type)
    controller = Controller(drone)

    root = tk.Tk()
    app = DroneApp(root, controller)
    root.mainloop()

main()


