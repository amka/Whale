# coding: utf-8
from Tkinter import Tk
from ttk import Frame


class App(object):
    def __init__(self):
        self.root = Tk()
        self.root.geometry('320x240')

        self.frame = Frame(master=self.root)

    def run(self):
        self.root.mainloop()
