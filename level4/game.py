from defines import Config
from seeker import Seeker
from hider import Hider

class Game:
    def __init__(self, gui, is_debug):
        self.__map = self.__n = self.__m = None
        self.__range_seek = Config.RANGE_SEEKER
        self.__range_hide = Config.RANGE_HIDER
        self.__gui = gui
        self.__num_hiders = 0
        self.__hiders = []
        self.__obs = []

    def read_input(self, map_name, is_debug):
        fin = open("../map/" + map_name + ".txt", "r")
        self.__n, self.__m = [int(x) for x in fin.readline().split(" ")]
        self.__read_map(fin)
        self.__read_obstacles(fin)
        if not is_debug:
            self.__gui.read_config(self.__map)
        self.__init_players()
        fin.close()

    def __get_agent_coord(self):
        seeker_coord, hider_coords = None, []
        for i in range(self.__n):
            for j in range(self.__m):
                if self.__map[i][j] == Config.SEEKER:
                    seeker_coord = (i, j)
                elif self.__map[i][j] == Config.HIDER:
                    hider_coords.append((i, j))
                    self.__num_hiders += 1
        return seeker_coord, hider_coords

    def __init_players(self):
        seeker_coord, hiders_coords = self.__get_agent_coord()
        self.__hiders = ([Hider(self.__map, self.__n, self.__m, self.__range_hide, hider_coord, seeker_coord, self.__obs) 
            for hider_coord in hiders_coords])
        self.__seeker = Seeker(self.__map, self.__n, self.__m, self.__range_seek, seeker_coord, self.__obs)
        self.__seeker.update_num_hiders(self.__num_hiders)

    def __read_map(self, fin):
        self.__map = [[int(x) for x in fin.readline().split(" ")] for i in range(self.__n)]

    def __read_obstacles(self, fin):
        line = fin.readline()
        while (line != ""):
            x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
            new_obs = []
            for i in range(x_tl, x_br + 1):
                for j in range(y_tl, y_br + 1):
                    self.__map[i][j] = Config.OBS
                    new_obs.append((i, j))
            self.__obs.append(new_obs)
            line = fin.readline()

    def __is_seeker_turn(self):
        return self.__turn % (self.__num_hiders + 1) == 1

    def __is_turn_of_hider_number(self):
        return (self.__turn % (self.__num_hiders + 1) - 2) % (self.__num_hiders + 1)

    def __compute_seeker_turn(self):
        res = (self.__turn - 1) // (self.__num_hiders + 1) + 1
        if (res < Config.PREGAME_TURN):
            res = -1
        return res

    def __compute_hider_turn(self, index):
        res = (self.__turn - (index + 2)) // (self.__num_hiders + 1) + 1
        if res < Config.PREGAME_TURN:
            res = -1
        return res

    def __hiders_found(self):
        for i in range(len(self.__hiders)):
            if self.__hiders[i] != None:
                return False
        return True

    def make_seeker_move(self):
        x, y = self.__seeker.move(self.__compute_seeker_turn())
        self.__point -= int(x != 0 or y != 0)
        self.__map[self.__seeker.cur_x - x][self.__seeker.cur_y - y] = Config.EMPTY
        self.__map[self.__seeker.cur_x][self.__seeker.cur_y] = Config.SEEKER
        for i in range(len(self.__hiders)):
            if self.__hiders[i] != None:
                self.__hiders[i].map[self.__seeker.cur_x - x][self.__seeker.cur_y - y] = Config.EMPTY
                self.__hiders[i].map[self.__seeker.cur_x][self.__seeker.cur_y] = Config.SEEKER

    def make_hider_move(self, is_debug):
        index_hider_move = self.__is_turn_of_hider_number()
        current_hider = self.__hiders[index_hider_move]
        if current_hider != None:
            x, y = current_hider.move(self.__compute_hider_turn(index_hider_move))
            self.__seeker.update_hider_pos(current_hider.cur_x, current_hider.cur_y, x, y)
            if not self.overlap_hider(self.__hiders[index_hider_move].cur_x - x, self.__hiders[index_hider_move].cur_y - y, index_hider_move):
                self.__map[self.__hiders[index_hider_move].cur_x - x][self.__hiders[index_hider_move].cur_y - y] = Config.EMPTY
            self.__map[self.__hiders[index_hider_move].cur_x][self.__hiders[index_hider_move].cur_y] = Config.HIDER
            if current_hider.should_announced(self.__compute_hider_turn(index_hider_move)):
                x, y = current_hider.announce()
                self.__seeker.signal_announce(x, y)
                if not is_debug:
                    self.__gui.send_signal_announce((x, y), self.__turn)

    def __is_time_out(self):
        return self.__turn >= Config.TIME_LIMIT

    def operate(self, is_debug):
        self.__turn, self.__point = (1, 0)
        self.__winner = Config.HIDER
        message = ""
        while True:
            if self.__hiders_found() and (self.__turn - 1) % (self.__num_hiders + 1) == 1:
                self.__winner = Config.SEEKER
                break
            if self.__is_time_out():
                message = "Time out"
                break
            if self.__seeker.visited_all():
                message = "Seeker gives up"
                break
            if self.__is_seeker_turn():
                self.make_seeker_move()
            else:
                self.make_hider_move(is_debug)
            self.update_game_info(is_debug)
        if not is_debug:
            self.__gui.visualize()
        if (self.__winner == Config.SEEKER):
            print("Seeker win")
        else:
            print(message + ", hiders win")
        print("Point: {:d}".format(self.__point))

    def update_game_info(self, is_debug):
        if not is_debug:
            self.__gui.update_map(self.__map)
        self.__turn += 1
        self.__check_met_hider(is_debug)

    def __notify_hiders(self):
        for hider in self.__hiders:
            if hider == None:
                continue
            is_regconized = False
            for hider_x, hider_y in self.__seeker.list_notify:
                if hider.cur_x == hider_x and hider.cur_y == hider_y:
                    is_regconized = True
                    hider.update_seeker_pos(self.__seeker.cur_x, self.__seeker.cur_y)
            hider.is_regconized = is_regconized

    def overlap_hider(self, i, j, index):
        for k in range(len(self.__hiders)):
            if self.__hiders[k] != None:
                if k != index:
                    if (self.__hiders[k].cur_x, self.__hiders[k].cur_y) == (i, j):
                        return True
        return False

    def __check_met_hider(self, is_debug):
        found_somehider = False
        for i in range(len(self.__hiders)):
            hider = self.__hiders[i]
            if hider != None:
                if self.__seeker.meet(hider):
                    if is_debug:
                        print("found hider at {} {}".format(self.__seeker.cur_x, self.__seeker.cur_y))
                        print(self.__turn)
                    self.__point += 20
                    x, y = hider.cur_x, hider.cur_y
                    if not self.overlap_hider(x, y, i):
                        self.__map[x][y] = Config.EMPTY
                        self.__seeker.map[x][y] = Config.VERIFIED
                    self.__hiders[i] = None
                    found_somehider = True
        if found_somehider:
            self.reset_seeker_info()

    def reset_seeker_info(self):
        self.__seeker.detected_coord = None
        self.__seeker.radar_path = []
        self.__seeker.announce = None
        self.__seeker.init_heuristic_map()
        self.__seeker.reset_verified_map()

    def check_observable(self, i, j):
        print(self.__seeker.is_observable(i, j))