from defines import *
import copy
import numpy as np

class Game:
    def __init__(self, gui):
        self.map = self.n = self.m = self.seeker = None
        self.seeker = []
        self.hider = []
        self.rangeSeek = 3
        self.rangeHide = 2
        self.gui = gui

    # <ReadInput>----------------------------------------

    def read_map(self, fin):
        self.map = [[int(x) for x in fin.readline().split(" ")] for i in range(self.n)]
        print('shape: ', np.shape(self.map))
    
    def init_map(self):
        for i in range(self.n):
            for j in range(self.m):
                if (self.map[i][j] == SEEKER):
                    self.seeker.append([i, j])
                    self.map[i][j] = EMPTY
                if (self.map[i][j] == HIDER):
                    self.hider.append([i, j])
                    self.map[i][j] = EMPTY

    def read_obstacles(self, fin):
        line = fin.readline()
        while (line != ""):
            # read coordinates of top left and bottom right of the rectangle obstacles
            x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
            x_br += 1
            y_br += 1
            for i in range(x_tl, x_br):
                for j in range(y_tl, y_br):
                    self.map[i][j] = OBS
            line = fin.readline()

    def read_input(self, map_name):
        with open("../map/" + map_name + ".txt", "r") as fin:
            self.n, self.m = map(int, fin.readline().split(' '))
            
            self.read_map(fin)
            self.read_obstacles(fin)
            self.gui.read_config(self.map)
            self.init_map()

            fin.close()
    
    # </ReadInput>-----------------------------------------

    # <GetterAndSetter>------------------------------------

    def getMap(self):
        return copy.deepcopy(self.map)
    
    def getSize(self):
        return self.n, self.m
    
    def getRangeHider(self):
        return self.rangeHide

    def getRangeSeeker(self):
        return self.rangeSeek

    def getSeekerLocation(self):
        return self.seeker

    def getHiderLocation(self):
        return self.hider

    def setHider(self, id, x, y):
        self.hider[id] = [x, y]

    def setSeeker(self, id, x, y):
        self.seeker[id] = [x, y]
    
    # </GetterAndSetter>------------------------------------

    def isMeet(self, x, y):
        for i in self.hider:
            if i == [x, y]:
                return True
        return False

    def printMap(self):
        for i in range(self.n):
            for j in range(self.m):
                if [i, j] in self.hider:
                    print("{:d}".format(HIDER), end = " ")
                elif [i, j] in self.seeker:
                    print("{:d}".format(SEEKER), end = " ")
                else:  
                    print("{:d}".format(self.map[i][j]), end = " ")
            print()