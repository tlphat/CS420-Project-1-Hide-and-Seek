import tkinter
import time
from PIL import Image, ImageTk

class Gui:
    def __init__(self):
        # canvas related fields
        self.windows_root = self.game_canvas = self.canvas_w = self.canvas_h = None
        self.img_wall = self.img_hider = self.img_seeker = self.img_obstacle = None
        # map config
        self.n = self.m = self.map = None
        self.moves = []
        # display config
        self.cell_size = 40
        self.move_id = -1

    def read_map(self, fin):
        self.map = [[0] * self.m for _ in range(self.n)]
        for i in range(self.n):
            self.map[i] = [int(x) for x in fin.readline().split(" ")]

    def read_obstacles(self, fin):
        line = fin.readline()
        while (line != ""):
            x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
            for i in range(x_tl, x_br):
                for j in range(y_tl, y_br):
                    self.map[i][j] = 4
            line = fin.readline()

    def read_input(self, map_name):
        with open("../map/" + map_name + ".txt", "r") as fin:
            self.n, self.m = [int(x) for x in fin.readline().split(" ")]
            self.read_map(fin)
            self.read_obstacles(fin)
            fin.close()

    def read_moves(self, move_name):
        with open("../move/" + move_name + ".txt", "r") as fin:
            line = fin.readline()
            while (line != ""):
                x, y = [int(x) for x in line.split(" ")]
                self.moves.append((x, y))
                line = fin.readline()
            fin.close()

    def init_image(self):
        self.img_wall = ImageTk.PhotoImage(Image.open("asset/wall.jpg"))
        self.img_hider = ImageTk.PhotoImage(Image.open("asset/hider.jpg"))
        self.img_seeker = ImageTk.PhotoImage(Image.open("asset/seeker.jpg"))
        self.img_obstacle = ImageTk.PhotoImage(Image.open("asset/obstacle.jpg"))

    def init_canvas(self):
        self.windows_root = tkinter.Tk()
        self.windows_root.title("Hide and Seek P2DK")
        self.canvas_w = self.cell_size * (self.m + 2)
        self.canvas_h = self.cell_size * (self.n + 2)
        self.game_canvas = tkinter.Canvas(self.windows_root, width = self.canvas_w, height = self.canvas_h, bg = "white")
        self.game_canvas.pack()

    def draw_lines(self):
        for column_x in range (self.cell_size, self.canvas_w, self.cell_size):
            self.game_canvas.create_line(column_x, 0, column_x, self.canvas_h)
        for row_y in range (self.cell_size, self.canvas_h, self.cell_size):
            self.game_canvas.create_line(0, row_y, self.canvas_w, row_y)

    def draw_borders(self):
        for column_x in range(0, self.canvas_w, self.cell_size):
            self.game_canvas.create_image(column_x + 1, 1, image = self.img_wall, anchor = "nw")
            self.game_canvas.create_image(column_x + 1, self.canvas_h - self.cell_size + 1, image = self.img_wall, anchor = "nw")

        for row_y in range(40, self.canvas_h - 40, 40):
            self.game_canvas.create_image(1, row_y + 1, image = self.img_wall, anchor = "nw")
            self.game_canvas.create_image(self.canvas_w - self.cell_size + 1, row_y + 1, image = self.img_wall, anchor = "nw")

    def draw_map(self):
        self.draw_lines()
        self.draw_borders()
        for i in range (self.n):
            for j in range(self.m):
                x = self.cell_size * (i + 1) + 1
                y = self.cell_size * (j + 1) + 1
                if self.map[i][j] == 1:
                    self.game_canvas.create_image(y, x, image = self.img_wall, anchor = "nw")
                elif self.map[i][j] == 2:
                    self.game_canvas.create_image(y, x, image = self.img_hider, anchor = "nw")
                elif self.map[i][j] == 3:
                    self.my_seeker = self.game_canvas.create_image(y, x, image = self.img_seeker, anchor = "nw")
                elif self.map[i][j] == 4:
                    self.game_canvas.create_image(y, x, image = self.img_obstacle, anchor = "nw")

    def move(self):
        self.move_id += 1
        x, y = self.moves[self.move_id]
        self.game_canvas.move(self.my_seeker, y * self.cell_size, x * self.cell_size)

    def move_process(self):
        time = 2000
        for _ in range(len(self.moves)):
            self.game_canvas.after(time, self.move)
            time += 1000

    def read_config(self, map_name, move_name):
        self.read_input(map_name)
        self.read_moves(move_name)

    def init_components(self):
        self.init_canvas()
        self.init_image()

    def visualize(self):
        self.init_components()
        self.draw_map()
        self.move_process()
        self.windows_root.mainloop()

if __name__ == "__main__":
    gui = Gui()
    gui.read_config("1.1", "sample_move")
    gui.visualize()