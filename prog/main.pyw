import tkinter as tk

from func import Covid
from GUImain import GUI

if __name__ == "__main__":
    prog = Covid()          # Program
    window = tk.Tk()        # Blank window
    gui = GUI(prog, window)  # Main Program with both prog and window
    gui.main()
