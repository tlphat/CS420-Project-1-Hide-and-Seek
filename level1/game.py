from defines import *
from seeker import Seeker
from hider import Hider

class Game:
    def __init__(self, gui):
        self.__map = self.__n = self.__m = None
        self.__range_seek = RANGE_SEEKER
        self.__range_hide = RANGE_HIDER
        self.__gui = gui

    def read_input(self, map_name):
        fin = open("../map/" + map_name + ".txt", "r")
        self.__n, self.__m = [int(x) for x in fin.readline().split(" ")]
        self.__read_map(fin)
        self.__read_obstacles(fin)
        self.__gui.read_config(self.__map)
        self.__init_players()
        fin.close()

    def __init_players(self):
        self.__seeker = Seeker(self.__map, self.__n, self.__m, self.__range_seek)
        self.__hider = Hider(self.__map, self.__n, self.__m, self.__range_hide)

    def __read_map(self, fin):
        self.__map = [[int(x) for x in fin.readline().split(" ")] for i in range(self.__n)]

    def __read_obstacles(self, fin):
        line = fin.readline()
        while (line != ""):
            x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
            for i in range(x_tl, x_br + 1):
                for j in range(y_tl, y_br + 1):
                    self.__map[i][j] = OBS
            line = fin.readline()

    def __is_seeker_turn(self):
        return self.__turn % 2 == 1

    def __hider_announce_turn(self):
        return (self.__turn // 2) % 5 == 0
        #return self.__hider.should_anounce()

    def operate(self):
        self.__turn, self.__point = (1, 0)
        self.__winner = HIDER
        while True:
            if self.__seeker.meet(self.__hider):
                self.__winner = SEEKER
                break
            if self.__seeker.visited_all():
                break
            if self.__is_seeker_turn():
                x, y = self.__seeker.move((self.__turn + 1) // 2)
                self.__point -= int(x != 0 or y != 0)
                self.__gui.append_move(x, y)
                self.__gui.append_observable(self.__seeker.obs_list)
            elif self.__hider_announce_turn():
                x, y = self.__hider.announce()
                self.__seeker.signal_announce(x, y)
                self.__gui.display_announce((x, y))
            self.__turn += 1
        self.__point += 20 * int(self.__winner == HIDER)
        self.__gui.visualize()
        if (self.__winner == SEEKER):
            print("Seeker win")
        else:
            print("Hider(s) win")
        print("Point: {:d}".format(self.__point))

    def check_observable(self, i, j):
        print(self.__seeker.is_observable(i, j))