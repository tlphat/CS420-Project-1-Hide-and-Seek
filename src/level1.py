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

#---------------------------------------------------------

class Seeker(Player):
    def __init__(self, map, size, range, location):
        super().__init__(map, size, range, location)
        self.hider = []
        self.annouce = []

    def next_move(self):
        if len(self.hider) > 0:
            if not self.directToCell(0, self.hider[0]):
                print('Find hider but do not have way to get there')
                exit(0)
            return
        if len(self.annouce) > 0:
            if not self.directToCell(0, self.annouce[0]):
                print('Get annouce but do not have way to get there')
                exit(0)
            return
        
        if self.turn < 5:
            return

        

    def updateAnnouce(self, location):
        i, j = location
        self.map[i][j] = ANNOUNCE
        if (self.isInsideRange(0, i, j)):
            self.annouce.append([i, j])
    
    def updateHider(self, i, j):
        self.hider.append([i, j])
        self.map[i][j] = HIDER

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
