from defines import Config
from player import Player
from queue import Queue
import heapq
import copy
import random

class Hider(Player):
    def __init__(self, map, n, m, obs_range, init_pos, seeker_init_pos):
        super().__init__(map, n, m, obs_range, init_pos)
        self.__seeker_init_pos = seeker_init_pos
        self.__cur_dest = init_pos
        self.cur_x, self.cur_y = init_pos
        self.__cur_step = None
#        self.__navigate()

    def __navigate(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == Config.HIDER:
                    self.cur_x, self.cur_y = i, j

    def should_announced(self):
        pass

    def move(self, turn):
        if self.__cur_dest == (self.cur_x, self.cur_y):
            self.__cur_dest = self.__find_dest((self.cur_x, self.cur_y))
            self.__cur_step = 0
        # print("Cur pos: {:d}, {:d}".format(self.cur_x, self.cur_y))
        # print("Path[0]: " + str(self.__cur_path[0]))
        # print("Cur des: " + str(self.__cur_dest))
        # print("Cur step: {:d}, Len curpath: {:d}".format(self.__cur_step, len(self.__cur_path)))
        next_move = self.__cur_path[self.__cur_step]
        x, y = next_move[0] - self.cur_x, next_move[1] - self.cur_y
        self.cur_x, self.cur_y = self.__cur_path[self.__cur_step]
        # print("Cur pos: {:d}, {:d}".format(self.cur_x, self.cur_y))
        self.__cur_step += 1
        return (x, y)

    def __mahattan_distance(self, src, des):
        x1, y1 = src
        x2, y2 = des
        return ((x2 - x1)**2 + (y2 - y1)**2)

    def __find_dest(self, src):

        class DestEntry:
            def __init__(self, pos, value):
                self.pos = pos
                self.value = value
            def __lt__(self, other):
                return self.value > other.value

        dest = []
        for i in range(self.n):
            for j in range(self.m):
                if i != self.cur_x and j != self.cur_y:
                    temp = 10 * self.hmap[i][j] - self.__mahattan_distance(src, (i,j))
                    heapq.heappush(dest, DestEntry((i,j), temp))

        while len(dest) != 0:
            des = heapq.heappop(dest).pos
            if self.__find_path(src, des) == True:
                return des
    
    def isAccessable(self, x, y):
        if x < 0 or x >= self.n:
            return False
        if y < 0 or y >= self.m:
            return False
        if self.map[x][y] in [Config.WALL, Config.OBS, Config.IMPOSSIBLE, Config.HIDER, Config.SEEKER]:
            return False
        return True

    def __BFS(self, src, des):
        path = [[-1, -1] * self.m for _ in range(self.n)]
        q = Queue()
        visited = [[False] * self.m for _ in range(self.n)]
        visited[self.cur_x][self.cur_y] = True
        q.put(src)
        while not q.empty():
            x, y = q.get()
            for dx, dy in Config.DIR:
                ux, uy = x + dx, y + dy
                if self.isAccessable(ux, uy) and not visited[ux][uy]:
                    visited[ux][uy] = True
                    q.put((ux, uy))
                    path[ux][uy] = x, y
                if (ux, uy) == des:
                    # print("src: "+str(src))
                    # print("ux: {:d}, uy: {:d}".format(ux, uy))
                    return path
        return None

    def __find_path(self, src, des):
        self.__cur_path = []
        path = self.__BFS(src, des)
        x,y = des
        if path != None:
            while path[x][y] != src:
                self.__cur_path.append(path[x][y])
                # print("x: {:d}, y: {:d}".format(x, y))
                # print("Path [x][y]: " + str(path[x][y]))
                x, y = path[x][y]
            self.__cur_path.append(des)
            return True
        return False
            
    def announce(self):
        x, y = self.__randomize()
        while (x < 0 or x >= self.n or y < 0 or y >= self.m or self.map[x][y] in [Config.WALL, Config.OBS]):
            x, y = self.__randomize()
        return (x, y)

    def __randomize(self):
        x = random.randint(self.cur_x - self.obs_range, self.cur_x + self.obs_range)
        y = random.randint(self.cur_y - self.obs_range, self.cur_y + self.obs_range)
        return (x, y)

    def meet(self, cur_x, cur_y):
        return (self.cur_x, self.cur_y) == (cur_x, cur_y)