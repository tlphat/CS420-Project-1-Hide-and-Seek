from defines import *
from gui_module import Gui
from game import Game
import copy
import random

if __name__ == "__main__":
    gui = Gui()
    game = Game(gui)
    game.read_input("1.1")
    game.operate()
