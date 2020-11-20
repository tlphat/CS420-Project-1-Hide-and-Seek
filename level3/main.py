from defines import Config
from gui_module import Gui
from game import Game
import copy
import random
import argparse
import time

debug_mode = False
map_name = ""

def parse_argument():
    global debug_mode, map_name
    parser = argparse.ArgumentParser()
    parser.add_argument("-ng", "--nongraphic", action = "store_true")
    parser.add_argument("-m", "--map")
    args = parser.parse_args()
    debug_mode = args.nongraphic
    map_name = args.map

if __name__ == "__main__":
    parse_argument()
    running_time = time.time()
    gui = Gui()
    game = Game(gui)
    game.read_input(map_name)
    game.operate(debug_mode)
    running_time = (time.time() - running_time) * 1000
    if debug_mode:
        print("Running time: {:f} ms".format(running_time))