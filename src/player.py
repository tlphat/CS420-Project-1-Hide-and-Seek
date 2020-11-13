import copy

class Player:
    def __init__(self, map, n, m, range):
        self.map = copy.deepcopy(map)
        self.n = n
        self.m = m
        self.turn = 0
        self.range = range
        self.X = self.Y = None

    def print_map(self): # use for debug
        for row in self.map:
            for i in row:
                print("{:d}".format(i), end = " ")
            print()

    def isInside(self, i, j):
        return (0 <= i and i < self.n and 0 <= j and j < self.m)

    def isInsideRange(self, i, j):
        return abs(i - self.X) <= self.range and abs(j - self.Y) <= self.range

    def updateLocation(self, i , j):
        self.X, self.Y = i, j

    def getLocation(self):
        return self.X, self.Y

    def UP(self):
        if (self.isInside(self.X - 1, self.Y)):
            self.updateLocation(self.X - 1, self.Y)

    def DOWN(self):
        if (self.isInside(self.X + 1, self.Y)):
            self.updateLocation(self.X + 1, self.Y)

    def LEFT(self):
        if (self.isInside(self.X, self.Y - 1)):
            self.updateLocation(self.X, self.Y - 1)

    def RIGHT(self):
        if (self.isInside(self.X, self.Y + 1)):
            self.updateLocation(self.X, self.Y + 1)