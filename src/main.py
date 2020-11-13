from defines import *
from level1 import Seeker, Hider

class Game:
    def __init__(self):        
        self.map = self.n = self.m = None
        self.seekX = self.seekY = self.hideX = self.hideY = None
        self.rangeSeek = 3
        self.rangeHide = 2

    def read_map(self, fin):
        self.map = [[0] * self.m for _ in range(self.n)]
        for i in range(self.n):
            self.map[i] = [int(x) for x in fin.readline().split(" ")]

    def read_obstacles(self, fin):
        line = fin.readline()
        while (line != ""):
            # read coordinates of top left and bottom right of the rectangle obstacles
            x_tl, y_tl, x_br, y_br = [int(x) for x in line.split(" ")]
            for i in range(x_tl, x_br):
                for j in range(y_tl, y_br):
                    self.map[i][j] = OBS
            line = fin.readline()

    def read_input(self):
        with open("../map/sample_map.txt", "r") as fin:
            self.n, self.m = [int(x) for x in fin.readline().split(" ")]

            self.read_map(fin)
            self.read_obstacles(fin)

            fin.close()

    def updateHider(self, i, j):
        self.hideX, self.hideY = i, j

    def updateSeeker(self, i, j):
        self.seekX, self.seekY = i, j

    def isMeet(self, i, j):
        return i == self.hideX and j == self.hideY

if __name__ == "__main__":
    game = Game()
    game.read_input()
    hider = Hider(game.map, game.n, game.m, game.rangeHide)
    seeker = Seeker(game.map, game.n, game.m, game.rangeSeek)
    #seeker.print_map()

    for i in range(10):
        seeker.next_move()
        hider.next_move()

        if hider.isAnnouce():
            seeker.updateAnnouce(hider.getAnnouce()[0], hider.getAnnouce()[1])
