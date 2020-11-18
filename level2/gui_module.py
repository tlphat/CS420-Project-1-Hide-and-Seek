from defines import *
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
        self.__moves = []
        self.__announce = []
        self.__observable = []
        # display config
        self.__cell_size = CELL_SIZE
        self.__move_id = -1
        self.__announce_id = -1
        self.__announce_signal = None
        self.__time_delay = TIME_DELAY

    def init_image(self):
        self.__img_wall = ImageTk.PhotoImage(Image.open("../asset/wall.jpg"))
        self.__img_hider = ImageTk.PhotoImage(Image.open("../asset/hider.jpg"))
        self.__img_seeker = ImageTk.PhotoImage(Image.open("../asset/seeker.jpg"))
        self.__img_obstacle = ImageTk.PhotoImage(Image.open("../asset/obstacle.jpg"))
        self.__img_announce = ImageTk.PhotoImage(Image.open("../asset/announce.jpg"))
        self.__img_observable = ImageTk.PhotoImage(Image.open("../asset/observable.jpg"))
        self.__img_emptycell = ImageTk.PhotoImage(Image.open("../asset/emptycell.jpg"))

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
                if self.__map[i][j] == 1:
                    self.__game_canvas.create_image(y, x, image = self.__img_wall, anchor = "nw")
                elif self.__map[i][j] == 2:
                    self.__game_canvas.create_image(y, x, image = self.__img_hider, anchor = "nw")
                elif self.__map[i][j] == 3:
                    self.__my_seeker = self.__game_canvas.create_image(y, x, image = self.__img_seeker, anchor = "nw")
                    self.__coord = (x, y)
                elif self.__map[i][j] == 4:
                    self.__game_canvas.create_image(y, x, image = self.__img_obstacle, anchor = "nw")

    def move(self):
        self.__move_id += 1
        x, y = self.__moves[self.__move_id]
        print("hello " + str(x) + " " + str(y))
        self.__game_canvas.move(self.__my_seeker, y * self.__cell_size, x * self.__cell_size)

    # def move(self):
    #     self.__move_id += 1
    #     if (self.__move_id != 0):
    #         print(self.__move_id - 1)
    #         prev_obs = self.__observable[self.__move_id - 1]
    #         for x, y in prev_obs:
    #             x = self.__cell_size * (x + 1) + 1
    #             y = self.__cell_size * (y + 1) + 1
    #             self.__game_canvas.create_image(y, x, image = self.__img_emptycell, anchor = "nw")
    #     cur_obs = self.__observable[self.__move_id]
    #     for x, y in cur_obs:
    #         x = self.__cell_size * (x + 1) + 1
    #         y = self.__cell_size * (y + 1) + 1
    #         self.__game_canvas.create_image(y, x, image = self.__img_observable, anchor = "nw")
    #     dx, dy = self.__moves[self.__move_id]
    #     x, y = self.__coord
    #     x, y = x + dx * self.__cell_size, y + dy * self.__cell_size
    #     self.__coord = x, y
    #     self.__game_canvas.create_image(y, x, image = self.__img_seeker, anchor = "nw")

    def fade_in_announce(self):
        self.__announce_id += 1
        i, j = self.__announce[self.__announce_id]
        x = self.__cell_size * (i + 1) + 1
        y = self.__cell_size * (j + 1) + 1
        self.__announce_signal = self.__game_canvas.create_image(y, x, image = self.__img_announce, anchor = "nw")

    def fade_out_announce(self):
        self.__game_canvas.delete(self.__announce_signal)

    def call_back(self):
        i, j = (0, 0)
        while True:
            if i >= len(self.__moves) and j >= len(self.__announce):
                break
            if i < len(self.__moves):
                self.__game_canvas.after(self.__time_delay * (2 * i + 1), self.move)
                i += 1
            if j < len(self.__announce):
                self.__game_canvas.after(10 * (j + 1) * self.__time_delay, self.fade_in_announce)
                self.__game_canvas.after((10 * (j + 1) + 1) * self.__time_delay, self.fade_out_announce)
                j += 1

    def move_process(self):
        time = self.__time_delay
        for _ in range(len(self.__moves)):
            if time % (10 * self.__time_delay) == 9 * self.__time_delay:
                self.__game_canvas.after(time, self.fade_in_announce)
                self.__game_canvas.after(time, self.fade_out_announce)
            #if time % (10 * self.__time_delay) == 0:
            self.__game_canvas.after(time, self.move)
            time += self.__time_delay
    
    def append_move(self, dx, dy):
        self.__moves.append((dx, dy))

    def display_announce(self, p):
        self.__announce.append((p[0][0], p[0][1]))

    def append_observable(self, observe_list):
        self.__observable.append(observe_list)

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
