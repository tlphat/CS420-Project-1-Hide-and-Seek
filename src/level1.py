from defines import *

class Seeker:
    def __init__(self, map, n, m):
        self.map = map
        self.n = n
        self.m = m
        self.eliminate_hider_pos()

    def eliminate_hider_pos(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] is HIDER:
                    self.map[i][j] = EMPTY

    def print_map(self): # use for debug
        for row in self.map:
            for i in row:
                print("{:d}".format(i), end = " ")
            print()

    def next_move(self):
        # main function implement here
        pass