from defines import Config
import tkinter
import time
import copy
from PIL import Image, ImageTk

class Gui:
    def __init__(self):
        # canvas related fields
        self.__windows_root = self.__game_canvas = self.__canvas_w = self.__canvas_h = None
        self.__img_wall = self.__img_hider = self.__img_seeker = self.__img_obstacle = None
        # map config
        self.__n = self.__m = self.__map = None
        self.__maps = []
        self.__map_id = 0
        self.__announce = []
        self.announce_signal = None
        self.__announce_id = -1
        # display config
        self.__cell_size = Config.CELL_SIZE
        self.__time_delay = Config.TIME_DELAY

    def init_image(self):
        self.__img_wall = ImageTk.PhotoImage(Image.open("../asset/wall.jpg"))
        self.__img_hider = ImageTk.PhotoImage(Image.open("../asset/hider.jpg"))
        self.__img_seeker = ImageTk.PhotoImage(Image.open("../asset/seeker.jpg"))
        self.__img_obstacle = ImageTk.PhotoImage(Image.open("../asset/obstacle.jpg"))
        self.__img_announce = ImageTk.PhotoImage(Image.open("../asset/announce.jpg"))
        self.__img_observable = ImageTk.PhotoImage(Image.open("../asset/observable.jpg"))
        self.__img_emptycell = ImageTk.PhotoImage(Image.open("../asset/emptycell.jpg"))
        self.__img_overlap = ImageTk.PhotoImage(Image.open("../asset/overlap.jpg"))
        self.__img_hider_obs = ImageTk.PhotoImage(Image.open("../asset/hiderobs.jpg"))

    def init_canvas(self):
        self.__windows_root = tkinter.Tk()
        self.__windows_root.title("Hide and Seek P2DK")
        self.__canvas_w = self.__cell_size * (self.__m + 2)
        self.__canvas_h = self.__cell_size * (self.__n + 2)
        self.__game_canvas = tkinter.Canvas(self.__windows_root, width = self.__canvas_w, height = self.__canvas_h, bg = "white")
        self.__game_canvas.pack()

    def draw_lines(self):
        for column_x in range (self.__cell_size, self.__canvas_w, self.__cell_size):
            self.__game_canvas.create_line(column_x, 0, column_x, self.__canvas_h)
        for row_y in range (self.__cell_size, self.__canvas_h, self.__cell_size):
            self.__game_canvas.create_line(0, row_y, self.__canvas_w, row_y)

    def draw_borders(self):
        for column_x in range(0, self.__canvas_w, self.__cell_size):
            self.__game_canvas.create_image(column_x + 1, 1, image = self.__img_wall, anchor = "nw")
            self.__game_canvas.create_image(column_x + 1, self.__canvas_h - self.__cell_size + 1, image = self.__img_wall, anchor = "nw")

        for row_y in range(self.__cell_size, self.__canvas_h - self.__cell_size, self.__cell_size):
            self.__game_canvas.create_image(1, row_y + 1, image = self.__img_wall, anchor = "nw")
            self.__game_canvas.create_image(self.__canvas_w - self.__cell_size + 1, row_y + 1, image = self.__img_wall, anchor = "nw")

    def draw_obs_hider(self, cur_map):
        for i in range(self.__n):
            for j in range(self.__m):
                if cur_map[i][j] == Config.HIDER:
                    for k in range(i - Config.RANGE_HIDER, i + Config.RANGE_HIDER + 1):
                        for t in range(j - Config.RANGE_HIDER, j + Config.RANGE_HIDER + 1):
                            if k >= 0 and k < self.__n and t >= 0 and t < self.__m and self.is_observable(i, j, k, t, Config.RANGE_HIDER):
                                x = self.__cell_size * (k + 1) + 1
                                y = self.__cell_size * (t + 1) + 1
                                self.__game_canvas.create_image(y, x, image = self.__img_hider_obs, anchor = "nw")

    def draw_obs_seeker(self, cur_map):
        for i in range(self.__n):
            for j in range(self.__m):
                if cur_map[i][j] == Config.SEEKER:
                    for k in range(i - Config.RANGE_SEEKER, i + Config.RANGE_SEEKER + 1):
                        for t in range(i - Config.RANGE_SEEKER, j + Config.RANGE_SEEKER + 1):
                            if k >= 0 and k < self.__n and t >= 0 and t < self.__m and self.is_observable(i, j, k, t, Config.RANGE_SEEKER):
                                x = self.__cell_size * (k + 1) + 1
                                y = self.__cell_size * (t + 1) + 1
                                self.__game_canvas.create_image(y, x, image = self.__img_observable, anchor = "nw")

    def draw_assets(self, cur_map):
        for i in range(self.__n):
            for j in range(self.__m):
                x = self.__cell_size * (i + 1) + 1
                y = self.__cell_size * (j + 1) + 1
                if cur_map[i][j] == Config.WALL:
                    self.__game_canvas.create_image(y, x, image = self.__img_wall, anchor = "nw")
                elif cur_map[i][j] == Config.HIDER:
                    self.__game_canvas.create_image(y, x, image = self.__img_hider, anchor = "nw")
                elif cur_map[i][j] == Config.SEEKER:
                    self.__my_seeker = self.__game_canvas.create_image(y, x, image = self.__img_seeker, anchor = "nw")
                elif cur_map[i][j] == Config.OBS:
                    self.__game_canvas.create_image(y, x, image = self.__img_obstacle, anchor = "nw")

    def draw_map(self):
        self.__game_canvas.delete("all")
        self.draw_lines()
        self.draw_borders()
        cur_map = self.__maps[self.__map_id]
        self.draw_obs_hider(cur_map)
        self.draw_obs_seeker(cur_map)
        self.draw_assets(cur_map)
        self.__map_id += 1

    def is_observable(self, x, y, i, j, obs_range):
        if x == i and y == j:
            return True
        if not(abs(i - x) <= obs_range and abs(j - y) <= obs_range):
            return False
        if (abs(i - x) + abs(j - y) < 2):
            return True
        if (i == x):
            return self.observe_horizontal(id, x, y, i, j)
        if (j == y):
            return self.observe_vertical(id, x, y, i, j)
        if (abs(x - i) == abs(y - j)):
            return self.observe_diagonal(id, x, y, i, j)
        if (abs(i - x) + abs(j - y) == 3):
            return self.observe_second_layer(x, y, i, j)
        return self.observe_odd_cases(id, x, y, i, j)

    def observe_second_layer(self, x, y, i, j):
        if abs(x - i) == 2:
            tx = (x + i) // 2
            return not (self.__maps[self.__map_id][tx][j] in [Config.WALL, Config.OBS])
        else:
            ty = (y + j) // 2
            return not (self.__maps[self.__map_id][i][ty] in [Config.WALL, Config.OBS])

    def observe_horizontal(self, id, x, y, i, j):
        for k in range(min(y, j), max(y, j)):
            if self.__maps[self.__map_id][x][k] in [Config.WALL, Config.OBS]:
                return False
        return True

    def observe_vertical(self, id, x, y, i, j):
        for k in range(min(x, i), max(x, i)):
            if self.__maps[self.__map_id][k][y] in [Config.WALL, Config.OBS]:
                return False
        return True

    def observe_diagonal(self, id, x, y, i, j):
        for k in range(min(i, x) + 1, max(i, x)):
            if (x - i) * (y - j) > 0:
                if self.__maps[self.__map_id][k][min(j, y) + k - min(x, i)] in [Config.WALL, Config.OBS]:
                    return False
            else:
                if self.__maps[self.__map_id][k][max(j, y) + min(x, i)  - k] in [Config.WALL, Config.OBS]:
                    return False
        return True

    def observe_odd_cases(self, id, x, y, i, j):
        if abs(x - i) == 3:
            if self.__maps[self.__map_id][x-1*(x-i)//abs(x-i)][j+(y-j)//abs(y-j)] in [Config.WALL, Config.OBS] or \
                self.__maps[self.__map_id][x-2*(x-i)//abs(x-i)][y-(y-j)//abs(y-j)] in [Config.WALL, Config.OBS]:
                return False
        else:
            if self.__maps[self.__map_id][i+(x-i)//abs(x-i)][y-1*(y-j)//abs(y-j)] in [Config.WALL, Config.OBS] or \
                self.__maps[self.__map_id][x-(x-i)//abs(x-i)][y-2*(y-j)//abs(y-j)] in [Config.WALL, Config.OBS]:
                return False
        return True

    def read_config(self, map):
        self.__maps.append(copy.deepcopy(map))
        self.__n, self.__m = len(map), len(map[0])
        self.init_components()

    def update_map(self, map):
        self.__maps.append(copy.deepcopy(map))

    def init_components(self):
        self.init_canvas()
        self.init_image()
        self.draw_map()

    def call_back(self):
        for i in range(len(self.__maps) - 1):
            self.__game_canvas.after((i + 1) * self.__time_delay, self.draw_map)

    def handle_announce(self):
        self.__announce_id += 1
        x, y, _ = self.__announce[self.__announce_id]
        tx = self.__cell_size * (x + 1) + 1
        ty = self.__cell_size * (y + 1) + 1
        self.announce_signal = self.__game_canvas.create_image(ty, tx, image = self.__img_announce, anchor = "nw")

    def eliminate_announce(self):
        self.__game_canvas.delete(self.announce_signal)

    def send_signal_announce(self, coords, turn):
        x, y = coords
        self.__announce.append((x, y, turn))

    def call_back_announce(self):
        for x, y, turn in self.__announce:
            self.__game_canvas.after(turn * self.__time_delay, self.handle_announce)
            self.__game_canvas.after((turn + 1) * self.__time_delay, self.eliminate_announce)

    def visualize(self):
        self.call_back()
        self.call_back_announce()
        self.__windows_root.mainloop()
