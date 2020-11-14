from defines import *
import random
import copy
from player import Player

def myRand(l, r, n):
    res = random.randint(l, r)
    if (res < 0):
        return 0
    if (res >= n):
        return n - 1
    return res

class Seeker(Player):
    def __init__(self, map, n, m, range):
        super().__init__(map, n, m, range)
        self.eliminate_hider_pos()

    def eliminate_hider_pos(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] is HIDER:
                    self.map[i][j] = EMPTY
                if self.map[i][j] is SEEKER:
                    self.X = i
                    self.Y = j

    def next_move(self):
        if HIDER in self.map:
            a = 1

        return

    def updateAnnouce(self, i, j):
        if (self.isInsideRange(i, j)):
            self.map[i][j] = ANNOUNCE
    
    def updateHider(self, i, j):
        self.map[i][j] = HIDER

#---------------------------------------------------

class Hider(Player):
    def __init__(self, map, n, m, range):
        super().__init__(map, n, m, range)
        self.annouceX = self.annouceY = None
        self.eliminate_seeker_pos()

    def eliminate_seeker_pos(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] is SEEKER:
                    self.map[i][j] = EMPTY
                if self.map[i][j] is HIDER:
                    self.X = i
                    self.Y = j

    def next_move(self):
        self.turn += 1
        if (self.turn % 5) == 0:
            self.annouce()
    
    def isAnnouce(self):
        return (self.turn % 5) == 0

    def getAnnouce(self):
        return self.annouceX, self.annouceY

    def annouce(self):
        self.annouceX = myRand(self.X - self.range, self.X + self.range, self.n)
        self.annouceY = myRand(self.Y - self.range, self.Y + self.range, self.m)
