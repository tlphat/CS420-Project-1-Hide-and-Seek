import copy

class Player:
    def __init__(self, game):
        self.map = copy.deepcopy(game.map)
        self.game = game # intentionally shallow copy
        self.n = game.n
        self.m = game.m
        self.turn = 0
        self.range = self.X = self.Y = None

    def print_map(self): # use for debug
        for row in self.map:
            for cell in row:
                print("{:d}".format(cell), end = " ")
            print()

    def isInside(self, i, j):
        return (0 <= i and i < self.n and 0 <= j and j < self.m)

    def isInsideRange(self, i, j):
        if not(abs(i - self.X) <= self.range and abs(j - self.Y) <= self.range):
            return False
        
        if i >= self.X and j >= self.Y:
            u, v = i - self.X, j - self.Y

    def updateLocation(self, i , j):
        self.X, self.Y = i, j

    def get_location(self):
        return self.X, self.Y

    def up(self):
        if (self.isInside(self.X - 1, self.Y)):
            self.updateLocation(self.X - 1, self.Y)

    def down(self):
        if (self.isInside(self.X + 1, self.Y)):
            self.updateLocation(self.X + 1, self.Y)

    def left(self):
        if (self.isInside(self.X, self.Y - 1)):
            self.updateLocation(self.X, self.Y - 1)

    def right(self):
        if (self.isInside(self.X, self.Y + 1)):
            self.updateLocation(self.X, self.Y + 1)

    def leftUp(self):
        if (self.isInside(self.X - 1, self.Y - 1)):
            self.updateLocation(self.X - 1, self.Y - 1)
            
    def rightUp(self):
        if (self.isInside(self.X - 1, self.Y + 1)):
            self.updateLocation(self.X - 1, self.Y + 1)

    def leftDown(self):
        if (self.isInside(self.X + 1, self.Y - 1)):
            self.updateLocation(self.X + 1, self.Y - 1)

    def rightDown(self):
        if (self.isInside(self.X + 1, self.Y + 1)):
            self.updateLocation(self.X + 1, self.Y + 1)
