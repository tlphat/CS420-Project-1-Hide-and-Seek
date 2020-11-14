class Player:
    def __init__(self, map, size, range, location):
        self.map = map
        self.n, self.m = size
        self.range = range
        self.turn = 0
        self.cell = location

    def print_map(self): # use for debug
        for row in self.map:
            for cell in row:
                print("{:d}".format(cell), end = " ")
            print()

    def isInside(self, i, j):
        return (0 <= i and i < self.n and 0 <= j and j < self.m)

    def isInsideRange(self, id, i, j):
        if not(abs(i - self.cell[id][0]) <= self.range and abs(j - self.cell[id][1]) <= self.range):
            return False
        
        if i >= self.cell[id][0] and j >= self.cell[id][1]:
            u, v = i - self.cell[id][0], j - self.cell[id][1]

    def updateLocation(self, id, i , j):
        self.cell[id] = [i, j]

    def getLocation(self, id):
        return self.cell[id]

    # <MOVING> -----------------------------------------

    def up(self, id):
        if (self.isInside(self.cell[id][0] - 1, self.cell[id][1])):
            self.updateLocation(id, self.cell[id][0] - 1, self.cell[id][1])

    def down(self, id):
        if (self.isInside(self.cell[id][0] + 1, self.cell[id][1])):
            self.updateLocation(id, self.cell[id][0] + 1, self.cell[id][1])

    def left(self, id):
        if (self.isInside(self.cell[id][0], self.cell[id][1] - 1)):
            self.updateLocation(id, self.cell[id][0], self.cell[id][1] - 1)

    def right(self, id):
        if (self.isInside(self.cell[id][0], self.cell[id][1] + 1)):
            self.updateLocation(id, self.cell[id][0], self.cell[id][1] + 1)

    def leftUp(self, id):
        if (self.isInside(self.cell[id][0] - 1, self.cell[id][1] - 1)):
            self.updateLocation(id, self.cell[id][0] - 1, self.cell[id][1] - 1)
            
    def rightUp(self, id):
        if (self.isInside(self.cell[id][0] - 1, self.cell[id][1] + 1)):
            self.updateLocation(id, self.cell[id][0] - 1, self.cell[id][1] + 1)

    def leftDown(self, id):
        if (self.isInside(self.cell[id][0] + 1, self.cell[id][1] - 1)):
            self.updateLocation(id, self.cell[id][0] + 1, self.cell[id][1] - 1)

    def rightDown(self, id):
        if (self.isInside(self.cell[id][0] + 1, self.cell[id][1] + 1)):
            self.updateLocation(id, self.cell[id][0] + 1, self.cell[id][1] + 1)

    # </MOVING> -----------------------------------------