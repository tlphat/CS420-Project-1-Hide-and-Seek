from defines import Config
import copy

class Player:
    def __init__(self, map, n, m, obs_range, init_pos, obs):
        self.n, self.m, self.obs_range = n, m, obs_range
        self.map = copy.deepcopy(map)
        self.cur_x, self.cur_y = init_pos
        self.init_heuristic_map()
        self.obs = obs

    def is_in_range(self, x, y):
        return x >= 0 and x < self.n and y >= 0 and y < self.m

    def push(self, obs_id, direction):
        x, y = direction
        for ox, oy in self.obs[obs_id]:
            nx, ny = ox + x, oy + y
            if self.map[nx][ny] in [Config.WALL, Config.OBS, Config.SEEKER, Config.HIDER]:
                return False # not pushable
        for ox, oy in self.obs[obs_id]:
            nx, ny = ox + x, oy + y
            self.map[ox][oy] = Config.VERIFIED
            self.map[nx][ny] = Config.OBS
            self.obs[obs_id] = (nx, ny)
        return True

    def is_pregame(self, turn):
        return turn < Config.PREGAME_TURN

    def is_observable(self, i, j):
        x, y = self.cur_x, self.cur_y
        if x == i and y == j:
            return True
        if not(abs(i - x) <= self.obs_range and abs(j - y) <= self.obs_range):
            return False
        if (abs(i - x) + abs(j - y) < 2):
            return True
        if (i == x):
            return self.observe_horizontal(id, i, j)
        if (j == y):
            return self.observe_vertical(id, i, j)
        if (abs(x - i) == abs(y - j)):
            return self.observe_diagonal(id, i, j)
        if (abs(i - x) + abs(j - y) == 3):
            return self.observe_second_layer(i, j)
        return self.observe_odd_cases(id, i, j)

    def observe_second_layer(self, i, j):
        x, y = self.cur_x, self.cur_y
        if abs(x - i) == 2:
            tx = (x + i) // 2
            return not (self.map[tx][j] in [Config.WALL, Config.OBS])
        else:
            ty = (y + j) // 2
            return not (self.map[i][ty] in [Config.WALL, Config.OBS])

    def observe_horizontal(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        for k in range(min(y, j), max(y, j)):
            if self.map[x][k] in [Config.WALL, Config.OBS]:
                return False
        return True

    def observe_vertical(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        for k in range(min(x, i), max(x, i)):
            if self.map[k][y] in [Config.WALL, Config.OBS]:
                return False
        return True

    def observe_diagonal(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        for k in range(min(i, x) + 1, max(i, x)):
            if (x - i) * (y - j) > 0:
                if self.map[k][min(j, y) + k - min(x, i)] in [Config.WALL, Config.OBS]:
                    return False
            else:
                if self.map[k][max(j, y) + min(x, i)  - k] in [Config.WALL, Config.OBS]:
                    return False
        return True

    def observe_odd_cases(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        if abs(x - i) == 3:
            if self.map[x-1*(x-i)//abs(x-i)][j+(y-j)//abs(y-j)] in [Config.WALL, Config.OBS] or \
                self.map[x-2*(x-i)//abs(x-i)][y-(y-j)//abs(y-j)] in [Config.WALL, Config.OBS]:
                return False
        else:
            if self.map[i+(x-i)//abs(x-i)][y-1*(y-j)//abs(y-j)] in [Config.WALL, Config.OBS] or \
                self.map[x-(x-i)//abs(x-i)][y-2*(y-j)//abs(y-j)] in [Config.WALL, Config.OBS]:
                return False
        return True

    def init_heuristic_map(self):
        self.hmap = [[0] * self.m for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] in [Config.EMPTY]:
                    self.hmap[i][j] = self.__count_nonempty_adj(i, j)

    def __count_nonempty_adj(self, i, j):
        cnt = 0
        for direction in Config.DIR:
            x, y = i + direction[0], j + direction[1]
            if x < 0 or x >= self.n or y < 0 or y >= self.m:
                continue
            cnt += int(self.map[x][y] in [Config.WALL, Config.OBS])
        return cnt