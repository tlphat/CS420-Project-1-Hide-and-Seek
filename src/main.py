from defines import *
from level1 import Seeker

map = n = m = None

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
                map[i][j] = OBS
        line = fin.readline()

def read_input():
    global n, m
    with open("../map/sample_map.txt", "r") as fin:
        n, m = [int(x) for x in fin.readline().split(" ")]
        read_map(fin)
        read_obstacles(fin)
        fin.close()

if __name__ == "__main__":
    read_input()
    seeker = Seeker(map, n, m)
    seeker.print_map()
