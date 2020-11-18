from defines import *
import copy

class Player:
    def __init__(self, map, n, m, obs_range):
        self.n, self.m, self.obs_range = n, m, obs_range
        self.map = copy.deepcopy(map)
        self.cur_x = self.cur_y = None

    def is_observable(self, i, j):
        x, y = self.cur_x, self.cur_y
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
            return not (self.map[tx][j] in [WALL, OBS])
        else:
            ty = (y + j) // 2
            return not (self.map[i][ty] in [WALL, OBS])

    def observe_horizontal(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        for k in range(min(y, j), max(y, j)):
            if self.map[x][k] in [WALL, OBS]:
                return False
        return True

    def observe_vertical(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        for k in range(min(x, i), max(x, i)):
            if self.map[k][y] in [WALL, OBS]:
                return False
        return True

    def observe_diagonal(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        for k in range(min(i, x) + 1, max(i, x)):
            if (x - i) * (y - j) > 0:
                if self.map[k][min(j, y) + k - min(x, i)] in [WALL, OBS]:
                    return False
            else:
                if self.map[k][max(j, y) + min(x, i)  - k] in [WALL, OBS]:
                    return False
        return True

    def observe_odd_cases(self, id, i, j):
        x, y = self.cur_x, self.cur_y
        if abs(x - i) == 3:
            if self.map[x-1*(x-i)//abs(x-i)][j+(y-j)//abs(y-j)] in [WALL, OBS] or \
                self.map[x-2*(x-i)//abs(x-i)][y-(y-j)//abs(y-j)] in [WALL, OBS]:
                return False
        else:
            if self.map[i+(x-i)//abs(x-i)][y-1*(y-j)//abs(y-j)] in [WALL, OBS] or \
                self.map[x-(x-i)//abs(x-i)][y-2*(y-j)//abs(y-j)] in [WALL, OBS]:
                return False
        return True