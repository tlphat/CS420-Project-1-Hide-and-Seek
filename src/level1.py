from defines import *
import random
from player import Player

def myRand(l, r, n):
    res = random.randint(l, r)
    if (res < 0):
        return 0
    if (res >= n):
        return n - 1
    return res

class Seeker(Player):
    def __init__(self, map, size, range, location):
        super().__init__(map, size, range, location)
        self.hider = []
        self.annouce = []

    def next_move(self):
        if HIDER in self.map:
            a = 1

        return

    def updateAnnouce(self, i, j):
        if (self.isInsideRange(0, i, j)):
            self.annouce.append([i, j])
    
    def updateHider(self, i, j):
        self.hider.append([i, j])

#---------------------------------------------------

class Hider(Player):
    def __init__(self, map, size, range, location):
        super().__init__(map, size, range, location)
        self.annouceX = self.annouceY = None

    def next_move(self):
        self.turn += 1
        if (self.turn % 5) == 0:
            self.annouce()
    
    def isAnnouce(self):
        return (self.turn % 5) == 0

    def getAnnouce(self):
        return self.annouceX, self.annouceY

    def annouce(self):
        for hider in self.cell:
            self.annouceX = myRand(hider[0] - self.range, hider[0] + self.range, self.n)
            self.annouceY = myRand(hider[1] - self.range, hider[1] + self.range, self.m)
