from defines import *
import numpy as np
import heapq

class Player:
    def __init__(self, map, size, range, location, gui):
        self.map = map
        self.n, self.m = size
        self.range = range
        self.turn = 0
        self.cell = location
        self.gui = gui
        self.move = 0

    def print_map(self): # use for debug
        for row in self.map:
            for cell in row:
                # print("{:d}".format(cell), end = " ")
                
                if cell in [WALL, OBS]:
                    print(cell, end = " ")
                elif cell == SEEKER:
                    print('S', end = " ")    
                elif cell == HIDER:
                    print('H', end = " ")
                elif cell == VERIFIED:
                    print('-', end = " ")
                elif cell ==VERIFIEDHIHI:
                    print('.', end= " ")
                elif cell == IMPOSSIBLE:
                    print('X', end = " ")
                else:
                    print(' ', end = " ")
                
                
            print()

    def isInsideMap(self, i, j):
        return (0 <= i and i < self.n and 0 <= j and j < self.m)

    def observe_second_layer(self, x, y, i, j):
        if abs(x - i) == 2:
            tx = (x + i) // 2
            return not (self.map[tx][j] in [WALL, OBS])
        else:
            ty = (y + j) // 2
            return not (self.map[i][ty] in [WALL, OBS])

    def observe_horizontal(self, x, y, i, j):
        for k in range(min(y, j), max(y, j)):
            if self.map[x][k] in [WALL, OBS]:
                return False
        return True

    def observe_vertical(self, x, y, i, j):
        for k in range(min(x, i), max(x, i)):
            if self.map[k][y] in [WALL, OBS]:
                return False
        return True

    def observe_diagonal(self, x, y, i, j):
        for k in range(min(i, x) + 1, max(i, x)):
            if (x - i) * (y - j) > 0:
                if self.map[k][min(j, y) + k - min(x, i)] in [WALL, OBS]:
                    return False
            else:
                if self.map[k][max(j, y) + min(x, i)  - k] in [WALL, OBS]:
                    return False
        return True

    def observe_odd_cases(self, x, y, i, j):
        if abs(x - i) == 3:
            if self.map[x-1*(x-i)//abs(x-i)][j+(y-j)//abs(y-j)] in [WALL, OBS] or \
                self.map[x-2*(x-i)//abs(x-i)][y-(y-j)//abs(y-j)] in [WALL, OBS]:
                return False
        else:
            if self.map[i+(x-i)//abs(x-i)][y-1*(y-j)//abs(y-j)] in [WALL, OBS] or \
                self.map[x-(x-i)//abs(x-i)][y-2*(y-j)//abs(y-j)] in [WALL, OBS]:
                return False
        return True

    def isInsideRange(self, u, v, i, j):
        obj = [u, v]
        if not(abs(i - obj[0]) <= self.range and abs(j - obj[1]) <= self.range):
            return False
        if (abs(i - obj[0]) + abs(j - obj[1]) < 2):
            return True
        if (i == obj[0]):
            return self.observe_horizontal(u, v, i, j)
        if (j == obj[1]):
            return self.observe_vertical(u, v, i, j)
        if (abs(obj[0] - i) == abs(obj[1] - j)):
            return self.observe_diagonal(u, v, i, j)
        if (abs(i - obj[0]) + abs(j - obj[1]) == 3):
            return self.observe_second_layer(u, v, i, j)
        return self.observe_odd_cases(u, v, i, j)

    def updateLocation(self, id, i , j):
        self.cell[id] = [i, j]

    def getLocation(self, id):
        return self.cell[id]

    def isExistThisStateAround(self, id, type):
        obj = self.cell[id]
        for i in range(max(0, obj[0] - self.range), min(self.n-1, obj[0] + self.range)):
            for j in range(max(0, obj[1] - self.range), min(self.m-1, obj[1] + self.range)):
                if (self.map[i][j] == id):
                    return True
        return False

    # <Direct> -----------------------------------------

    def directToCell(self, id, target):
        if (self.cell[id] == target):
            return True

        # dijkstra heap

        d = np.full((self.n, self.m), float('infinity'))
        pre = [[ [-1, -1] for j in range(self.m)] for i in range(self.n)]
        u, v = self.cell[id]
        d[u][v] = 0

        pq = [(0, [u, v])]

        while len(pq) > 0:
            du, [u, v] = heapq.heappop(pq)

            if du != d[u][v]:
                continue

            if [u, v] == target:
                break

            for direct in DIR:
                uu, vv = u + direct[0], v + direct[1]

                if not self.isInsideMap(uu, vv) or not self.isInsideRange(u, v, uu, vv) or self.map[uu][vv] in [OBS, WALL]:
                    continue

                if du + 1 < d[uu][vv]:
                    d[uu][vv] = du + 1
                    pre[uu][vv] = [u, v]
                    #print('pre[',uu,'][',vv,'] =',pre[uu][vv])
                    heapq.heappush(pq, (d[uu][vv], [uu, vv]))
        
        # backtrack

        u, v = target

        if pre[u][v] == [-1, -1]:
            return False

        while pre[u][v] != self.cell[id]:
            # print('pre[',u,'][',v,']=',pre[u][v])
            u, v = pre[u][v]

        # print('Direct:', u, v)

        self.movingByDirect(id, [u - self.cell[id][0], v - self.cell[id][1]])

        return True
    
    def movingByDirect(self, id, direct):
        i, j = direct
        for dir in range(8):
            if (DIR[dir] == [i, j]):
                self.gui.append_move(DIR[dir][0], DIR[dir][1])
                if (dir == 0):
                    self.leftUp(id)
                elif (dir == 1):
                    self.up(id)
                elif (dir == 2):
                    self.rightUp(id)
                elif (dir == 3):
                    self.right(id)
                elif (dir == 4):
                    self.rightDown(id)
                elif (dir == 5):
                    self.down(id)
                elif (dir == 6):
                    self.leftDown(id)
                elif (dir == 7):
                    self.left(id)
                break

    # </Direct> ----------------------------------------

    # <MOVING> -----------------------------------------

    def up(self, id):
        if (self.isInsideMap(self.cell[id][0] - 1, self.cell[id][1])):
            self.updateLocation(id, self.cell[id][0] - 1, self.cell[id][1])

    def down(self, id):
        if (self.isInsideMap(self.cell[id][0] + 1, self.cell[id][1])):
            self.updateLocation(id, self.cell[id][0] + 1, self.cell[id][1])

    def left(self, id):
        if (self.isInsideMap(self.cell[id][0], self.cell[id][1] - 1)):
            self.updateLocation(id, self.cell[id][0], self.cell[id][1] - 1)

    def right(self, id):
        if (self.isInsideMap(self.cell[id][0], self.cell[id][1] + 1)):
            self.updateLocation(id, self.cell[id][0], self.cell[id][1] + 1)

    def leftUp(self, id):
        if (self.isInsideMap(self.cell[id][0] - 1, self.cell[id][1] - 1)):
            self.updateLocation(id, self.cell[id][0] - 1, self.cell[id][1] - 1)
            
    def rightUp(self, id):
        if (self.isInsideMap(self.cell[id][0] - 1, self.cell[id][1] + 1)):
            self.updateLocation(id, self.cell[id][0] - 1, self.cell[id][1] + 1)

    def leftDown(self, id):
        if (self.isInsideMap(self.cell[id][0] + 1, self.cell[id][1] - 1)):
            self.updateLocation(id, self.cell[id][0] + 1, self.cell[id][1] - 1)

    def rightDown(self, id):
        if (self.isInsideMap(self.cell[id][0] + 1, self.cell[id][1] + 1)):
            self.updateLocation(id, self.cell[id][0] + 1, self.cell[id][1] + 1)

    # </MOVING> -----------------------------------------