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
        self.__moves_seeker = []
        self.__moves_hiders = []
        self.__announce = []
        self.__observable_seeker = []
        self.__observable_hiders = []
        self.__coord_hiders = []
        self.__coord_seeker = None
        # display config
        self.__cell_size = Config.CELL_SIZE
        self.__move_id = -1
        self.__announce_id = -1
        self.__announce_signal = None
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

    def draw_map(self):
        self.draw_lines()
        self.draw_borders()
        for i in range (self.__n):
            for j in range(self.__m):
                x = self.__cell_size * (i + 1) + 1
                y = self.__cell_size * (j + 1) + 1
                if self.__map[i][j] == Config.WALL:
                    self.__game_canvas.create_image(y, x, image = self.__img_wall, anchor = "nw")
                elif self.__map[i][j] == Config.HIDER:
                    self.__game_canvas.create_image(y, x, image = self.__img_hider, anchor = "nw")
                    self.__coord_hiders.append((x, y))
                    self.__observable_hiders.append([])
                    self.__moves_hiders.append([])
                elif self.__map[i][j] == Config.SEEKER:
                    self.__my_seeker = self.__game_canvas.create_image(y, x, image = self.__img_seeker, anchor = "nw")
                    self.__coord_seeker = (x, y)
                elif self.__map[i][j] == Config.OBS:
                    self.__game_canvas.create_image(y, x, image = self.__img_obstacle, anchor = "nw")

    def __delete_previous_seeker_observable_range(self):
        if (self.__move_id != 0 and self.__move_id <= len(self.__observable_seeker)):
            prev_obs = self.__observable_seeker[self.__move_id - 1]
            for x, y in prev_obs:
                x = self.__cell_size * (x + 1) + 1
                y = self.__cell_size * (y + 1) + 1
                self.__game_canvas.create_image(y, x, image = self.__img_emptycell, anchor = "nw")

    def __mark_current_seeker_observable_range(self, marked_cells):
        cur_obs = self.__observable_seeker[self.__move_id]
        for x, y in cur_obs:
            marked_cells.add((x, y))
            x = self.__cell_size * (x + 1) + 1
            y = self.__cell_size * (y + 1) + 1
            self.__game_canvas.create_image(y, x, image = self.__img_observable, anchor = "nw")

    def __delete_previous_hiders_observable_ranges(self, marked_cells):
        for i in range(len(self.__coord_hiders)):
            if (self.__move_id != 0 and self.__move_id <= len(self.__observable_hiders[i])):
                prev_obs = self.__observable_hiders[i][self.__move_id - 1]
                for x, y in prev_obs:
                    if (x, y) not in marked_cells:
                        x = self.__cell_size * (x + 1) + 1
                        y = self.__cell_size * (y + 1) + 1
                        self.__game_canvas.create_image(y, x, image = self.__img_emptycell, anchor = "nw")

    def __mark_current_hiders_observable_ranges(self, marked_cells):
        for i in range(len(self.__coord_hiders)):
            if not self.__hider_is_dead(i):
                cur_obs = self.__observable_seeker[self.__move_id]
                for x, y in cur_obs:
                    tx = self.__cell_size * (x + 1) + 1
                    ty = self.__cell_size * (y + 1) + 1
                    if (x, y) in marked_cells:
                        self.__game_canvas.create_image(ty, tx, image = self.__img_overlap, anchor = "nw")
                    else:
                        self.__game_canvas.create_image(ty, tx, image = self.__img_hider_obs, anchor = "nw")

    def __draw_current_hiders(self):
        for i in range(len(self.__coord_hiders)):
            if not self.__hider_is_dead(i):
                dx, dy = self.__moves_hiders[i]
                x, y = self.__coord_hiders[i]
                x, y = x + dx * self.__cell_size, y + dy * self.__cell_size
                self.__coord_hiders[i] = (x, y)
                self.__game_canvas.create_image(y, x, image = self.__img_hider, anchor = "nw")

    def __draw_currente_seeker(self):
        dx, dy = self.__moves_seeker[self.__move_id]
        x, y = self.__coord_seeker
        x, y = x + dx * self.__cell_size, y + dy * self.__cell_size
        self.__coord_seeker = x, y
        self.__game_canvas.create_image(y, x, image = self.__img_seeker, anchor = "nw")

    def move(self):
        self.__move_id += 1
        marked_cells = set()
        self.__delete_previous_seeker_observable_range()
        self.__mark_current_seeker_observable_range(marked_cells)
        self.__delete_previous_hiders_observable_ranges(marked_cells)
        self.__mark_current_hiders_observable_ranges(marked_cells)
        self.__draw_current_hiders()
        self.__draw_currente_seeker()

    def fade_in_announce(self):
        self.__announce_signals = []
        for i in range(len(self.__coord_hiders)):
            if not self.__hider_is_dead(i):
                self.__announce_id += 1
                i, j = self.__announce[self.__announce_id]
                x = self.__cell_size * (i + 1) + 1
                y = self.__cell_size * (j + 1) + 1
                signal = self.__game_canvas.create_image(y, x, image = self.__img_announce, anchor = "nw")
                self.__announce_signals.append(signal)

    def fade_out_announce(self):
        for signal in self.__announce_signals:
            self.__game_canvas.delete(signal)

    def call_back(self):
        i = j = 0
        while True:
            if i >= len(self.__moves_seeker) and j >= len(self.__announce):
                break
            if i < len(self.__moves_seeker):
                self.__game_canvas.after(self.__time_delay * (2 * i + 1), self.move)
                i += 1
            if j < len(self.__announce):
                self.__game_canvas.after(10 * (j + 1) * self.__time_delay, self.fade_in_announce)
                self.__game_canvas.after((10 * (j + 1) + 1) * self.__time_delay, self.fade_out_announce)
                j += len(self.__coord_hiders)

    def move_process(self):
        time = self.__time_delay
        for _ in range(len(self.__moves_seeker)):
            if time % (10 * self.__time_delay) == 9 * self.__time_delay:
                self.__game_canvas.after(time, self.fade_in_announce)
                self.__game_canvas.after(time, self.fade_out_announce)
            self.__game_canvas.after(time, self.move)
            time += self.__time_delay
    
    def append_move_seeker(self, dx, dy):
        self.__moves_seeker.append((dx, dy))

    def append_move_hider(self, index, dx, dy):
        self.__moves_hiders[index].append((dx, dy))

    def display_announce(self, p):
        self.__announce.append(p)

    def append_observable_seeker(self, observe_list):
        self.__observable_seeker.append(observe_list)

    def append_observable_hider(self, index, observe_list):
        self.__observable_hiders[index].append(observe_list)

    def make_hider_die(self, index):
        self.__coord_hiders[index] = (-1, -1)

    def __hider_is_dead(self, index):
        return self.__coord_hiders[index] == (-1, -1)

    def read_config(self, map):
        self.__map = copy.deepcopy(map)
        self.__n, self.__m = len(map), len(map[0])
        self.init_components()

    def init_components(self):
        self.init_canvas()
        self.init_image()

    def visualize(self):
        self.draw_map()
        self.call_back()
        self.__windows_root.mainloop()
