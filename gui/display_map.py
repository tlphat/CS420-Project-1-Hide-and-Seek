import tkinter
import time
from PIL import Image, ImageTk

# canvas
root = my_canvas = width_canvas = height_canvas = None

# map
n = m = map = None

# image
image_wall_block = image_hider = image_seeker = image_obstacle = None

# movements
movements = None

# seeker
my_seeker = None

def read_input():
    global n, m
    with open("map/sample_map.txt", "r") as fin:
        n, m = [int(x) for x in fin.readline().split(" ")]

        read_map(fin)
        read_obstacles(fin)

        fin.close()

def read_moves():
    global movements
    movements = []
    with open("move/sample_move.txt", "r") as fin:
        line = fin.readline()
        while (line != ""):
            x, y = [int(x) for x in line.split(" ")]
            movements.append((x, y))
            line = fin.readline()
        fin.close()

def read_map(fin):
    global map
    map = [[0] * m for _ in range(n)]
    for i in range(n):
        map[i] = [int(x) for x in fin.readline().split(" ")]

def read_obstacles(fin):
    global map
    line = fin.readline()
    while (line != ""):
        # read coordinates of top left and bottom right of the rectangle obstacles
        x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
        for i in range(x_tl, x_br):
            for j in range(y_tl, y_br):
                map[i][j] = 4
        line = fin.readline()

def init_image():
    global image_hider, image_obstacle, image_seeker, image_wall_block
    image_wall_block = ImageTk.PhotoImage(Image.open("gui/asset/wall.jpg"))
    image_hider = ImageTk.PhotoImage(Image.open("gui/asset/hider.jpg"))
    image_seeker = ImageTk.PhotoImage(Image.open("gui/asset/seeker.jpg"))
    image_obstacle = ImageTk.PhotoImage(Image.open("gui/asset/obstacle.jpg"))

def init_canvas():
    global root, my_canvas, width_canvas, height_canvas
    root = tkinter.Tk()
    root.title("Hide and Seek P2DK")
    width_canvas = m*40 + 80
    height_canvas = n*40 + 80
    my_canvas = tkinter.Canvas(root, width = width_canvas, height = height_canvas, bg = "white")
    my_canvas.pack() # pady

def draw_lines():
    for column_x in range (40, width_canvas, 40):
        my_canvas.create_line(column_x, 0, column_x, height_canvas)
    for row_y in range (40, height_canvas, 40):
        my_canvas.create_line(0, row_y, width_canvas, row_y)

def draw_borders():
    for column_x in range(0, width_canvas, 40):
        my_canvas.create_image(column_x + 1, 1, image = image_wall_block, anchor = "nw")
        my_canvas.create_image(column_x + 1, height_canvas - 39, image = image_wall_block, anchor = "nw")

    for row_y in range(40, height_canvas - 40, 40):
        my_canvas.create_image(1, row_y + 1, image = image_wall_block, anchor = "nw")
        my_canvas.create_image(width_canvas - 39, row_y + 1, image = image_wall_block, anchor = "nw")

def draw_map():
    global my_seeker
    draw_lines()
    draw_borders()
    for i in range (n):
        for j in range(m):
            x = 40 * (i + 1) + 1
            y = 40 * (j + 1) + 1
            if map[i][j] == 1:
                my_canvas.create_image(x, y, image = image_wall_block, anchor = "nw")
            elif map[i][j] == 2:
                my_canvas.create_image(x, y, image = image_hider, anchor = "nw")
            elif map[i][j] == 3:
                my_seeker = my_canvas.create_image(x, y, image = image_seeker, anchor = "nw")
            elif map[i][j] == 4:
                my_canvas.create_image(x, y, image = image_obstacle, anchor = "nw")

direction = {
    (0, 0): "stay",
    (0, 1): "right",
	(0, -1): "left",
    (1, 0): "down",
    (-1, 0): "up",
    (1, 1): "right down",
    (-1, -1): "left up",
    (-1, 1): "right up",
	(1, -1): "left down"
}

index = -1
def mmove():
    global index
    index +=1
    x,y = movements[index]
    my_canvas.move(my_seeker, x*40, y*40)

def move_process():
    time = 2000
    for _ in range(len(movements)):
        my_canvas.after(time, mmove)
        time += 1000
        
def print_map(): # use for debug
    for row in map:
        for i in row:
            print("{:d}".format(i), end = " ")
        print()


if __name__ == "__main__":
    read_input()
    read_moves()
    init_canvas()
    init_image()
    draw_map()
    move_process()
    #print_map()
    root.mainloop()