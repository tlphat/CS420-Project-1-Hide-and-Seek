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

    def is_inside(self, i, j):
        return (0 <= i and i < self.n and 0 <= j and j < self.m)

    def is_inside_range(self, i, j):
        return abs(i - self.X) <= self.range and abs(j - self.Y) <= self.range

    def update_location(self, i , j):
        self.X, self.Y = i, j

    def get_location(self):
        return self.X, self.Y

    def up(self):
        if (self.is_inside(self.X - 1, self.Y)):
            self.update_location(self.X - 1, self.Y)

    def down(self):
        if (self.is_inside(self.X + 1, self.Y)):
            self.update_location(self.X + 1, self.Y)

    def left(self):
        if (self.is_inside(self.X, self.Y - 1)):
            self.update_location(self.X, self.Y - 1)

    def right(self):
        if (self.is_inside(self.X, self.Y + 1)):
            self.update_location(self.X, self.Y + 1)
