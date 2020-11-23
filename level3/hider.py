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
        self.__init_seeker_heuristic_map()
        self.__approximate_seeker_delay = 10
        self.obs_list = [] # list of current observable cells
#        self.__navigate()

    def __navigate(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == Config.HIDER:
                    self.cur_x, self.cur_y = i, j
    
    def __init_seeker_heuristic_map(self):
        self.__BFS_seeker_map = [[-1] * self.m for _ in range(self.n)]
        visited = [[False] * self.m for _ in range(self.n)]
        q = Queue()
        seeker_x, seeker_y = self.__seeker_init_pos
        visited[seeker_x][seeker_y] = True
        self.__BFS_seeker_map[seeker_x][seeker_y] = 0
        q.put((seeker_x, seeker_y, 0))
        while not q.empty():
            x, y, cost = q.get()
            for dx, dy in Config.DIR:
                ux, uy = x + dx, y + dy
                if not self.isAccessable(ux, uy) or visited[ux][uy]:
                    continue
                self.__BFS_seeker_map[ux][uy] = cost + 1
                visited[ux][uy] = True
                q.put([ux, uy, cost + 1])

    def should_announced(self):
        pass

    def move(self, turn):
        if self.__cur_dest == (self.cur_x, self.cur_y):
            if turn > self.__BFS_seeker_map[self.cur_x][self.cur_y] + self.__approximate_seeker_delay:
                return (0, 0)
            self.__cur_dest = self.__find_dest((self.cur_x, self.cur_y))
            self.__cur_step = 0
        x, y = self.__cur_path[self.__cur_step]
        #### avoid conflict
        # if self.map[x][y] == Config.HIDER: # meet another hider on the way
        #     if (x, y) == self.__cur_dest:
        #         return (0,0)
        #     alter_path = self.__BFS((self.cur_x, self.cur_y), (x,y))
        #     alter_path.pop() # pop the des from path
        #     self.__cur_path = alter_path + self.__cur_path
        #     x, y = self.__cur_path[self.__cur_step]
        dx, dy = x - self.cur_x, y - self.cur_y
        self.cur_x, self.cur_y = x, y
        self.__update_observable_range()
        self.__cur_step += 1
        return (dx, dy)

    def __update_observable_range(self):
        self.obs_list = []
        for i in range(self.cur_x - self.obs_range, self.cur_x + self.obs_range + 1):
            for j in range(self.cur_y - self.obs_range, self.cur_y + self.obs_range + 1):
                if i < 0 or i >= self.n or j < 0 or j >= self.m:
                    continue
                if self.is_observable(i, j) and self.map[i][j] not in [Config.WALL, Config.OBS]:
                    self.obs_list.append((i, j))

    def __mahattan_distance(self, src, des):
        x1, y1 = src
        x2, y2 = des
        return ((x2 - x1)**2 + (y2 - y1)**2)

    def __heuristic_value(self, src, i, j):
        return 10 * self.hmap[i][j] - self.__mahattan_distance(src, (i,j)) + self.__BFS_seeker_map[i][j]

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
                    heapq.heappush(dest, DestEntry((i,j), self.__heuristic_value(src, i,j)))

        while len(dest) != 0:
            des = heapq.heappop(dest).pos
            temp_path = self.__find_path(src, des)
            if temp_path != None:
                self.__cur_path = temp_path
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
        temp_path = []
        BFS_path = self.__BFS(src, des)
        x,y = des
        if BFS_path != None:
            while BFS_path[x][y] != src:
                temp_path.append(BFS_path[x][y])
                # print("x: {:d}, y: {:d}".format(x, y))
                # print("Path [x][y]: " + str(path[x][y]))
                x, y = BFS_path[x][y]
            temp_path.append(des)
            return temp_path
        return None
            
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