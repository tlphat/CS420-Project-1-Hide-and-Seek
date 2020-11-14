from defines import *
from level1 import Seeker, Hider

class Game:
    def __init__(self):
        self.map = self.n = self.m = self.seeker = None
        self.seekX = self.seekY = self.hideX = self.hideY = None
        self.rangeSeek = 3
        self.rangeHide = 2
        self.hider = []

    def seeker_register(self, seeker):
        self.seeker = seeker # intentionally shallow copy

    def hider_register(self, hider):
        self.hider.append(hider)

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

    def update_hider(self, x, y):
        self.hideX, self.hideY = x, y

    def update_seeker(self, x, y):
        self.seekX, self.seekY = x, y

    def is_meet(self, x, y):
        return (self.hideX, self.hideY) == (x, y)

    def send_announce(self, x, y):
        seeker.update_announce(x, y)

if __name__ == "__main__":
    game = Game()
    game.read_input()
    hider = Hider(game)
    seeker = Seeker(game)

    for i in range(200):
        seeker.next_move()
        hider.next_move()

        if hider.isAnnouce():
            seeker.updateAnnouce(hider.getAnnouce()[0], hider.getAnnouce()[1])

            print(hider.getAnnouce())
        
        if seeker.isInsideRange(hider.getLocation()):
            
