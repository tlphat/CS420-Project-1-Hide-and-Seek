from defines import *
import random
from player import Player
import numpy as np
import heapq

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
        self.heuristic = np.zeros((self.n, self.m))

        self.initHeuristic()
    
    def calcHeuristic(self, i, j):
        calc = 0
        for dir in DIR:
            u, v = i + dir[0], j + dir[1]
            if not self.isInsideMap(u, v) or self.map[u][v] != EMPTY:
                calc += 1
        return calc

    def initHeuristic(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.isInsideRange(0, i, j) or self.map[i][j] == WALL or self.map[i][j] == OBS:
                    self.heuristic[i][j] = float('infinity')
                    continue
                self.heuristic[i][j] = self.calcHeuristic(i, j)
                
    def fillHeuristic(self):
        obj = self.cell[0]
        for i in range(max(0, obj[0] - self.range), min(self.n-1, obj[0] + self.range)):
            for j in range(max(0, obj[1] - self.range), min(self.m-1, obj[1] + self.range)):
                if (self.map[i][j] == EMPTY):
                    self.map[i][j] = VERIFIED
                    self.heuristic[i][j] = float('infinity')

    def minHeuristicInRange(self):
        curH = float('infinity')
        u = v = None
        obj = self.cell[0]
        for i in range(max(0, obj[0] - 2*self.range-1), min(self.n-1, obj[0] + 2*self.range+1)):
            for j in range(max(0, obj[1] - 2*self.range-1), min(self.m-1, obj[1] + 2*self.range+1)):
                if (self.map[i][j] == EMPTY):
                    if (curH > self.heuristic[i][j]):
                        curH = self.heuristic[i][j]
                        u, v = i, j
        if (u == None):
            return u
        return u, v

    def next_move(self):
        print()
        print()
        print(self.cell[0])
        if len(self.hider) > 0:
            print('Goto hider')
            if not self.directToCell(0, self.hider[0]):
                print('Find hider but do not have way to get there')
                exit(0)
            return

        print('Not find hider yet')
        
        if len(self.annouce) > 0:
            print('Goto annouce')
            if not self.directToCell(0, self.annouce[0]):
                print('Get annouce but do not have way to get there')
                exit(0)
            return

        print('Not annouce yet')
        
        self.turn += 1
        if self.turn % 5 != 0:
            print('Waiting in turn ', self.turn)
            return
        else:
            print('Mark all neighbor are empty')
            self.fillHeuristic()

        print('Start to find min neighbor heuristic')

        target = self.minHeuristicInRange()

        print('Finish find neighbor heuristic')

        if target != None:
            print('neighbor heuristic not none:', target)
            if not self.directToCell(0, target):
                print('You never want this sentence appear')
                exit(0)
            return
        
        print('neighbor none')

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
