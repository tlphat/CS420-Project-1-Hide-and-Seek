from defines import *
from player import Player
import copy
import random

class Hider(Player):
    def __init__(self, map, n, m, obs_range):
        self.n, self.m, self.obs_range = n, m, obs_range
        self.map = copy.deepcopy(map)
        self.__navigate()

    def __navigate(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == HIDER:
                    self.cur_x, self.cur_y = i, j

    def announce(self):
        x, y = self.__randomize()
        while (x < 0 or x >= self.n or y < 0 or y >= self.m or self.map[x][y] in [WALL, OBS]):
            x, y = self.__randomize()
        return (x, y)

    def __randomize(self):
        x = random.randint(self.cur_x - self.obs_range, self.cur_x + self.obs_range)
        y = random.randint(self.cur_y - self.obs_range, self.cur_y + self.obs_range)
        return (x, y)

    def meet(self, cur_x, cur_y):
        return (self.cur_x, self.cur_y) == (cur_x, cur_y)