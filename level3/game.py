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
        hiders_coors = []
        seeker_coor = None
        for i in range(self.__n):
            for j in range(self.__m):
                if self.__map[i][j] == Config.SEEKER:
                    seeker_coor = i,j
                    self.__seeker = Seeker(self.__map, self.__n, self.__m, self.__range_seek, seeker_coor)
                elif self.__map[i][j] == Config.HIDER:
                    hiders_coors.append((i,j))
                    self.__num_hiders += 1

        for i in range(self.__num_hiders):
            self.__hiders.append(Hider(self.__map, self.__n, self.__m, self.__range_hide, hiders_coors[i], seeker_coor))
            print("init hider {:d}: ".format(i)+str(hiders_coors[i]))

        self.__seeker.update_num_hiders(self.__num_hiders)

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
        for _ in range(350):
            if self.__hiders_found():
                self.__winner = Config.SEEKER
                break
            if self.__seeker.visited_all():
                break
            if self.__is_seeker_turn():
                x, y = self.__seeker.move(self.__compute_seeker_turn())
                self.__point -= int(x != 0 or y != 0)
                print("Seeker: " + str(self.__seeker.cur_x) + " " + str(self.__seeker.cur_y))
                self.__map[self.__seeker.cur_x - x][self.__seeker.cur_y - y] = Config.EMPTY
                self.__map[self.__seeker.cur_x][self.__seeker.cur_y] = Config.SEEKER
            else:
                index_hider_move = self.__is_turn_of_hider_number()
                current_hider = self.__hiders[index_hider_move]
                if current_hider != None:
                    x, y = current_hider.move(self.__compute_hider_turn(index_hider_move))
                    print("Hider " + str(index_hider_move) + ": " + str(self.__hiders[index_hider_move].cur_x) + " " + str(self.__hiders[index_hider_move].cur_y))
                    self.__seeker.update_hider_pos(current_hider.cur_x, current_hider.cur_y, x, y)
                    if not self.overlap_hider(self.__hiders[index_hider_move].cur_x - x, self.__hiders[index_hider_move].cur_y - y, index_hider_move):
                        self.__map[self.__hiders[index_hider_move].cur_x - x][self.__hiders[index_hider_move].cur_y - y] = Config.EMPTY
                    self.__map[self.__hiders[index_hider_move].cur_x][self.__hiders[index_hider_move].cur_y] = Config.HIDER
                    if current_hider.should_announced(self.__compute_hider_turn(index_hider_move)):
                        x, y = current_hider.announce()
                        self.__seeker.signal_announce(x, y)
                        self.__gui.send_signal_announce((x, y), self.__turn)
                        #self.__gui.display_announce((x, y))
            self.__gui.update_map(self.__map)
            self.__turn += 1
            self.__check_met_hider()
        if not is_debug:
            self.__gui.visualize()
        if (self.__winner == Config.SEEKER):
            print("Seeker win")
        else:
            print("Hiders win")
        print("Point: {:d}".format(self.__point))

    def overlap_hider(self, i, j, index):
        for k in range(len(self.__hiders)):
            if self.__hiders[k] != None:
                if k != index:
                    if (self.__hiders[k].cur_x, self.__hiders[k].cur_y) == (i, j):
                        return True
        return False

    def __check_met_hider(self):
        for i in range(len(self.__hiders)):
            hider = self.__hiders[i]
            if hider != None:
                if self.__seeker.meet(hider):
                    self.__point += 20
                    x, y = hider.cur_x, hider.cur_y
                    if not self.overlap_hider(x, y, i):
                        self.__map[x][y] = Config.EMPTY
                    hider = None

    def check_observable(self, i, j):
        print(self.__seeker.is_observable(i, j))