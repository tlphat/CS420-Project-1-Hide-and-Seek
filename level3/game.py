from defines import Config
from seeker import Seeker
from hider import Hider

class Game:
    def __init__(self, gui):
        self.__map = self.__n = self.__m = None
        self.__range_seek = Config.RANGE_SEEKER
        self.__range_hide = Config.RANGE_HIDER
        self.__gui = gui
        self.__num_hiders = 0

    def read_input(self, map_name):
        fin = open("../map/" + map_name + ".txt", "r")
        self.__n, self.__m = [int(x) for x in fin.readline().split(" ")]
        self.__read_map(fin)
        self.__read_obstacles(fin)
        self.__gui.read_config(self.__map)
        self.__init_players()
        fin.close()

    def __init_players(self):
        self.__hiders = []
        for i in range(self.__n):
            for j in range(self.__m):
                if self.__map[i][j] == Config.SEEKER:
                    self.__seeker = Seeker(self.__map, self.__n, self.__m, self.__range_seek, (i, j))
                elif self.__map[i][j] == Config.HIDER:
                    self.__num_hiders += 1
                    self.__hiders.append(Hider(self.__map, self.__n, self.__m, self.__range_seek, (i, j)))

    def __read_map(self, fin):
        self.__map = [[int(x) for x in fin.readline().split(" ")] for i in range(self.__n)]

    def __read_obstacles(self, fin):
        line = fin.readline()
        while (line != ""):
            x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
            for i in range(x_tl, x_br + 1):
                for j in range(y_tl, y_br + 1):
                    self.__map[i][j] = Config.OBS
            line = fin.readline()

    def __is_seeker_turn(self):
        return self.__turn % (self.__num_hiders + 1) == 1

    def __is_turn_of_hider_number(self):
        return (self.__turn % (self.__num_hiders + 1) - 2) % (self.__num_hiders + 1)

    def __compute_seeker_turn(self):
        return (self.__turn - 1) // (self.__num_hiders + 1) + 1

    def __compute_hider_turn(self, index):
        return (self.__turn - (index + 2)) // (self.__num_hiders + 1) + 1

    def __hiders_found(self):
        return self.__num_hiders == 0

    def operate(self, is_debug):
        self.__turn, self.__point = (1, 0)
        self.__winner = Config.HIDER
        while True:
            if self.__hiders_found():
                self.__winner = Config.SEEKER
                break
            if self.__seeker.visited_all():
                break
            if self.__is_seeker_turn():
                x, y = self.__seeker.move(self.__compute_seeker_turn())
                self.__point -= int(x != 0 or y != 0)
                self.__gui.append_move(x, y)
                self.__gui.append_observable(self.__seeker.obs_list)
            else:
                index_hider_move = self.__is_turn_of_hider_number()
                current_hider = self.__hiders[index_hider_move]
                current_hider.move(self.__compute_hider_turn(index_hider_move))
                if current_hider.should_announced():
                    x, y = current_hider.announce()
                    self.__seeker.signal_announce(x, y)
                    self.__gui.display_announce((x, y))
            self.__turn += 1
            self.__check_met_hider()
        if not is_debug():
            self.__gui.visualize()
        if (self.__winner == Config.SEEKER):
            print("Seeker win")
        else:
            print("Hiders win")
        print("Point: {:d}".format(self.__point))

    def __check_met_hider(self):
        for hider in self.__hiders:
            if self.__seeker.meet(hider):
                self.__point += 20
                self.__hiders.remove(hider)

    def check_observable(self, i, j):
        print(self.__seeker.is_observable(i, j))