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

def mahattan(i, j, u, v):
    return abs(i - u) + abs(j - v)

#---------------------------------------------------------

class Seeker(Player):
    def __init__(self, map, size, range, location, gui):
        super().__init__(map, size, range, location, gui)
        self.hider = []
        self.annouce = []
        self.heuristic = np.zeros((self.n, self.m))

        self.initHeuristic()
        self.buildHeuristic()
        self.hiderFound = 0
    
    def printHeuristic(self):
        for row in self.heuristic:
            for cell in row:
                print(cell, end = " ")
            print()
    
    def calcHeuristic(self, i, j):
        calc = 0
        for dir in DIR:
            u, v = i + dir[0], j + dir[1]
            if not self.isInsideMap(u, v) or self.map[u][v] != EMPTY or self.heuristic[i][j] == float('infinity'):
                calc += 1
        return calc
    
    def initHeuristic(self):
        d = np.full((self.n, self.m), float('infinity'))
        pre = [[ [-1, -1] for j in range(self.m)] for i in range(self.n)]
        u, v = self.cell[0]
        d[u][v] = 0
        pq = [(0, [u, v])]

        while len(pq) > 0:
            du, [u, v] = heapq.heappop(pq)
            if du != d[u][v]:
                continue
            for direct in DIR:
                uu, vv = u + direct[0], v + direct[1]
                if not self.isInsideMap(uu, vv) or not self.isInsideRange(u, v, uu, vv) or self.map[uu][vv] in [OBS, WALL]:
                    continue
                if du + 1 < d[uu][vv]:
                    d[uu][vv] = du + 1
                    pre[uu][vv] = [u, v]
                    #print('pre[',uu,'][',vv,'] =',pre[uu][vv])
                    heapq.heappush(pq, (d[uu][vv], [uu, vv]))
        
        for i in range(self.n):
            for j in range(self.m):
                if d[i][j] == float('infinity') and self.map[i][j] not in [OBS, WALL]:
                    self.heuristic[i][j] = float('infinity')
                    self.map[i][j] = IMPOSSIBLE

    def buildHeuristic(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == WALL or self.map[i][j] == OBS or self.cell[0] == [i, j] or self.heuristic[i][j] == float('infinity'):
                    self.heuristic[i][j] = float('infinity')
                    continue
                self.heuristic[i][j] = self.calcHeuristic(i, j)
                
    def fillHeuristic(self):
        obj = self.cell[0]
        for i in range(max(0, obj[0] - self.range), min(self.n-1, obj[0] + self.range)):
            for j in range(max(0, obj[1] - self.range), min(self.m-1, obj[1] + self.range)):
                if self.map[i][j] == EMPTY and self.isInsideRange(obj[0], obj[1], i, j):
                    self.heuristic[i][j] = float('infinity')
                    if self.map[i][j] != HIDER:
                        self.map[i][j] = VERIFIEDHIHI

    def minHeuristicInRange(self):
        curH = float('infinity')
        u = v = None
        obj = self.cell[0]
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == VERIFIED or self.map[i][j] == VERIFIEDHIHI:
                    continue

                if u != None and self.heuristic[i][j] == curH and mahattan(obj[0], obj[1], u, v) > mahattan(obj[0], obj[1], i, j):
                    u, v = i, j

                if self.heuristic[i][j] < curH:
                    curH = self.heuristic[i][j]
                    u, v = i, j
        return u, v
                
    def next_move(self):
        if self.map[self.cell[0][0]][self.cell[0][1]] != HIDER:
            self.map[self.cell[0][0]][self.cell[0][1]] = VERIFIED

        # print()
        # print()
        # print('start in next move:',self.cell[0])
        if len(self.hider) > 0:
            k = None
            for i in range(len(self.hider)):
                if self.hider[i] != None:
                    k = i
                    break
            
            if k != None:
                if not self.directToCell(0, self.hider[k]):
                    self.hider[k] = None
                else:
                    self.move += 1
                    self.map[self.cell[0][0]][self.cell[0][1]] = SEEKER

                    self.fillHeuristic()
                    self.buildHeuristic()
                    # print('Goto hider', self.hider[k])
                    if self.cell[0] == self.hider[k]:
                        self.hider.remove(self.hider[k])
                        self.hiderFound += 1
                        self.map[self.cell[0][0]][self.cell[0][1]] = HIDER
                        print('Find hider: ', self.cell[0])
                    
                    return

        # print('Not find hider yet')
        
        if len(self.annouce) > 0:
            k = None
            for i in range(len(self.annouce)):
                if self.annouce[i] != None:
                    k = i
                    break
            
            if k != None:
                # print('Goto annouce:', self.annouce[k])
                if not self.directToCell(0, self.annouce[k]):
                    self.annouce[k] = None
                else:                    
                    self.move += 1

                    self.fillHeuristic()
                    self.buildHeuristic()

                    if self.map[self.cell[0][0]][self.cell[0][1]] != HIDER:
                        self.map[self.cell[0][0]][self.cell[0][1]] = SEEKER

                    if self.cell[0] == self.annouce[k]:
                        self.annouce[k] = None

                    return

        # print('Not annouce yet')
        
        self.turn += 1
        if self.turn <= 5 or self.turn % 5 != 1:
            # print('Waiting in turn ', self.turn)
            return
        else:
            # print('Mark all neighbor are empty')
            self.fillHeuristic()
            self.buildHeuristic()

        # print('Start to find min neighbor heuristic')

        target = self.minHeuristicInRange()

        # print('Finish find neighbor heuristic')

        if target != [None, None]:
            # print('neighbor heuristic not none:', target)
            if not self.directToCell(0, target):
                self.map[self.cell[0][0]][self.cell[0][1]] = SEEKER
                print('You never want this sentence appear:', target)
                print(self.print_map())
                exit(0)
            self.move += 1

            if self.map[self.cell[0][0]][self.cell[0][1]] != HIDER:
                self.map[self.cell[0][0]][self.cell[0][1]] = SEEKER
            return
        
        print('neighbor none')
        exit(0)

    def updateAnnouce(self, location):
        for it in location:
            i, j = it
            if (self.isInsideRange(self.cell[0][0], self.cell[0][1], i, j)):
                self.annouce.append([i, j])
    
    def updateHider(self, i, j):
        self.hider.append([i, j])
        self.map[i][j] = HIDER

#---------------------------------------------------

class Hider(Player):
    def __init__(self, map, size, range, location, gui):
        super().__init__(map, size, range, location, gui)
        self.listAnnouce = []

    def next_move(self):
        self.turn += 1
        if (self.turn % 5) == 0:
            self.annouce()
    
    def isAnnouce(self):
        return (self.turn % 5) == 0

    def getAnnouce(self):
        return self.listAnnouce

    def annouce(self):
        self.listAnnouce.clear()
        for hider in self.cell:
            u = myRand(hider[0] - self.range, hider[0] + self.range, self.n)
            v = myRand(hider[1] - self.range, hider[1] + self.range, self.m)

            while not self.isInsideRange(hider[0], hider[1], u, v) or self.map[u][v] in [OBS, WALL]:
                u = myRand(hider[0] - self.range, hider[0] + self.range, self.n)
                v = myRand(hider[1] - self.range, hider[1] + self.range, self.m)
                
            self.listAnnouce.append([u, v])
