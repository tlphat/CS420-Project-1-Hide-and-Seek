from defines import *
from player import Player
import copy

class Seeker(Player):
    def __init__(self, map, n, m, obs_range):
        super().__init__(map, n, m, obs_range)
        self.detected_coord = self.announce = None
        self.path = []
        self.radar_path = []
        self.__modify_map()
        self.__init_heuristic_map()

    def __init_heuristic_map(self):
        self.hmap = [[0] * self.m for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] in [EMPTY]:
                    self.hmap[i][j] = self.__count_nonempty_adj(i, j)

    def __count_nonempty_adj(self, i, j):
        cnt = 0
        for direction in DIR:
            x, y = i + direction[0], j + direction[1]
            if x < 0 or x >= self.n or y < 0 or y >= self.m:
                continue
            cnt += int(self.map[x][y] in [WALL, OBS])
        return cnt

    def __modify_map(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == SEEKER:
                    self.cur_x, self.cur_y = i, j
                    self.map[i][j] = VERIFIED

    def move(self, turn):
        self.__scan_verify()
        if self.detected_coord != None:
            if len(self.path) == 0:
                x, y = self.detected_coord
                self.path = copy.deepcopy(self.__find_path(x, y))
            x, y = self.path.pop(0)
            self.cur_x += x
            self.cur_y += y
            return (x, y)
        if self.announce is None and (turn is 1 or turn % 5 is not 1):
            return (0, 0)
        self.__cross_out_redundent_path()
        if len(self.radar_path) is 0:
            self.__explore()
        x, y = self.radar_path.pop(0)
        self.cur_x += x
        self.cur_y += y
        return (x, y)

    def __cross_out_redundent_path(self):
        for step in self.radar_path:
            x, y = step
            if self.map[x][y] is VERIFIED:
                self.radar_path = []
                return

    def __explore(self):
        x = y = None
        cur_heuristic = -1
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] not in [VERIFIED, WALL, OBS]:
                    comp_heuristic = self.hmap[i][j] * 10 - abs(self.cur_x - i) - abs(self.cur_y - j)
                    if comp_heuristic > cur_heuristic:
                        cur_heuristic = comp_heuristic
                        x, y = i, j
        self.radar_path = self.__find_path(x, y)

    def __scan_verify(self):
        for i in range(self.cur_x - self.obs_range, self.cur_x + self.obs_range + 1):
            for j in range(self.cur_y - self.obs_range, self.cur_y + self.obs_range + 1):
                if i < 0 or i >= self.n or j < 0 or j >= self.m:
                    continue
                if self.is_observable(i, j):
                    if (self.map[i][j] == HIDER):
                        self.detected_coord = (i, j)
                    elif self.map[i][j] not in [WALL, OBS]:
                        self.map[i][j] = VERIFIED

    def __find_path(self, fx, fy):
        queue = [(self.cur_x, self.cur_y, -1, -1)]
        visited_map = [[(-2, -2)] * self.m for _ in range(self.n)]
        visited_map[self.cur_x][self.cur_y] = (-1, -1)
        while len(queue) != 0:
            x, y, _, _ = queue.pop(0)
            if (x, y) == (fx, fy):
                break
            for direction in DIR:
                nxt_x, nxt_y = x + direction[0], y + direction[1]
                if nxt_x < 0 or nxt_x >= self.n:
                    continue
                if nxt_y < 0 or nxt_y >= self.m:
                    continue
                if self.map[nxt_x][nxt_y] in [WALL, OBS]:
                    continue
                if visited_map[nxt_x][nxt_y] != (-2, -2):
                    continue
                visited_map[nxt_x][nxt_y] = (x, y)
                queue.append((nxt_x, nxt_y, x, y))
        for i in range(self.n):
            for j in range(self.m):
                print(visited_map[i][j], end = " ")
            print()
        for i in range(self.n):
            for j in range(self.m):
                print(self.map[i][j], end = " ")
            print()
        res = []
        prev_x, prev_y = fx, fy
        x, y = visited_map[prev_x][prev_y]
        while (x, y) != (-1, -1):
            res.append((prev_x - x, prev_y - y))
            prev_x, prev_y = x, y
            x, y = visited_map[prev_x][prev_y]
        res.reverse()
        print(res)
        return res

    def signal_announce(self, x, y):
        if self.announce == None and self.__is_hearable(x, y):
            self.announce = (x, y)
            self.radar_path = []
            for i in range(x - 3, x + 4):
                for j in range(y - 3, y + 4):
                    if (self.map[i][j] not in [VERIFIED, WALL, OBS]):
                        self.hmap[i][j] = 99999999

    def __is_hearable(self, x, y):
        return abs(self.cur_x - x) <= self.obs_range and abs(self.cur_y - y) <= self.obs_range

    def meet(self, seeker):
        return seeker.meet(self.cur_x, self.cur_y)