from defines import *
from player import Player
import copy

class Seeker(Player):
    def __init__(self, map, n, m, obs_range):
        super().__init__(map, n, m, obs_range)
        self.detected_coord = self.announce = None
        self.path = []
        self.radar_path = []
        self.obs_list = []
        self.__modify_map()
        self.__init_heuristic_map()
        self.__visited_cells = 1
        self.__count_possible_cells()
        self.__should_give_up = False
        self.__scan_verify()

    def __count_possible_cells(self):
        self.__possible_cells = 0
        queue = [(self.cur_x, self.cur_y)]
        visited_map = [[False] * self.m for _ in range(self.n)]
        visited_map[self.cur_x][self.cur_y] = True
        while len(queue) != 0:
            tmp_x, tmp_y = queue.pop(0)
            self.__possible_cells += 1
            for dx, dy in DIR:
                nxt_x, nxt_y = tmp_x + dx, tmp_y + dy
                if self.is_in_range(nxt_x, nxt_y) and not visited_map[nxt_x][nxt_y] and self.map[nxt_x][nxt_y] not in [WALL, OBS]:
                    queue.append((nxt_x, nxt_y))
                    visited_map[nxt_x][nxt_y] = True
        self.__mark_unreachable_cell(visited_map)
        
    def __mark_unreachable_cell(self, visited_map):
        for i in range(self.n):
            for j in range(self.m):
                if not visited_map[i][j] and self.map[i][j] not in [VERIFIED, WALL, OBS]:
                    self.map[i][j] = IMPOSSIBLE

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

    def __make_a_move(self, x, y):
        self.cur_x += x
        self.cur_y += y
        self.__scan_verify()
        return (x, y)

    def __has_seen_announce(self):
        return self.announce != None

    def __is_turn_to_move(self, turn):
        return turn != 1 and turn % 5 == 1

    def __found_hider(self):
        return self.detected_coord != None

    def move(self, turn):
        if self.__found_hider():
            if len(self.path) == 0:
                x, y = self.detected_coord
                self.path = copy.deepcopy(self.__find_path(x, y))
            x, y = self.path.pop(0)
            return self.__make_a_move(x, y)
        
        if not self.__has_seen_announce() and not self.__is_turn_to_move(turn):
            return (0, 0)
        if not self.__has_seen_announce():
            self.__cross_out_redundent_path()
        if len(self.radar_path) == 0:
            self.__explore()
        if len(self.radar_path) == 0:
            if self.__has_checked_all_announce():
                self.__should_give_up = True
            return (0, 0)
        x, y = self.radar_path.pop(0)
        return self.__make_a_move(x, y)

    def __has_checked_all_announce(self):
        if not self.__has_seen_announce():
            return False
        for i in range(self.n):
            for j in range(self.m):
                if self.hmap[i][j] == SIGNAL_HEURISTIC and self.map[i][j] != VERIFIED:
                    return True
        return False

    def visited_all(self):
        print("visited_cells: {:d}".format(self.__visited_cells))
        print("possible_cells: {:d}".format(self.__possible_cells))
        print(self.cur_x, self.cur_y)
        if not self.__should_give_up and self.__visited_cells == self.__possible_cells:
            self.__should_give_up = True
        return self.__should_give_up

    def __cross_out_redundent_path(self):
        prev_x, prev_y = self.cur_x, self.cur_y
        for step in self.radar_path:
            x, y = step
            if self.map[prev_x + x][prev_y + y] != VERIFIED:
                return
            prev_x += x
            prev_y += y
        self.radar_path = []

    def __explore(self):
        x = y = None
        cur_heuristic = -10000000
        for i in range(self.n):
            for j in range(self.m):
                if self.hmap[i][j] == SIGNAL_HEURISTIC or self.map[i][j] not in [IMPOSSIBLE, VERIFIED, WALL, OBS]:
                    comp_heuristic = self.hmap[i][j] * 8 - abs(self.cur_x - i) - abs(self.cur_y - j)
                    if comp_heuristic > cur_heuristic:
                        cur_heuristic = comp_heuristic
                        x, y = i, j
        self.radar_path = self.__find_path(x, y)

    def __scan_verify(self):
        self.obs_list = []
        for i in range(self.cur_x - self.obs_range, self.cur_x + self.obs_range + 1):
            for j in range(self.cur_y - self.obs_range, self.cur_y + self.obs_range + 1):
                if i < 0 or i >= self.n or j < 0 or j >= self.m:
                    continue
                if self.is_observable(i, j):
                    if (self.map[i][j] == HIDER):
                        self.detected_coord = (i, j)
                    elif self.map[i][j] not in [IMPOSSIBLE, WALL, OBS]:
                        if self.map[i][j] != VERIFIED:
                            self.__visited_cells += 1
                            self.map[i][j] = VERIFIED
                        if (i, j) != (self.cur_x, self.cur_y):
                            self.obs_list.append((i, j))

    def __find_path(self, fx, fy):
        queue = [(self.cur_x, self.cur_y, -1, -1)]
        visited_map = [[(-2, -2)] * self.m for _ in range(self.n)]
        visited_map[self.cur_x][self.cur_y] = (-1, -1)
        can_find_path = False
        while len(queue) != 0:
            x, y, _, _ = queue.pop(0)
            if (x, y) == (fx, fy):
                can_find_path = True
                break
            for dx, dy in DIR:
                nxt_x, nxt_y = x + dx, y + dy
                if nxt_x < 0 or nxt_x >= self.n:
                    continue
                if nxt_y < 0 or nxt_y >= self.m:
                    continue
                if self.map[nxt_x][nxt_y] in [WALL, OBS, IMPOSSIBLE]:
                    continue
                if visited_map[nxt_x][nxt_y] != (-2, -2):
                    continue
                visited_map[nxt_x][nxt_y] = (x, y)
                queue.append((nxt_x, nxt_y, x, y))
        if not can_find_path:
            print("h {:d} {:d}".format(fx, fy))
            return []
        # trace back the path
        res = []
        prev_x, prev_y = fx, fy
        x, y = visited_map[prev_x][prev_y]
        while (x, y) != (-1, -1):
            res.append((prev_x - x, prev_y - y))
            prev_x, prev_y = x, y
            x, y = visited_map[prev_x][prev_y]
        res.reverse()
        return res

    def signal_announce(self, x, y):
        if self.announce == None and self.__is_hearable(x, y):
            self.announce = (x, y)
            self.radar_path = []
            for i in range(x - 3, x + 4):
                for j in range(y - 3, y + 4):
                    if not self.is_in_range(i, j):
                        continue
                    if (self.map[i][j] not in [VERIFIED, WALL, OBS]):
                        self.hmap[i][j] = SIGNAL_HEURISTIC

    def __is_hearable(self, x, y):
        return abs(self.cur_x - x) <= self.obs_range and abs(self.cur_y - y) <= self.obs_range

    def meet(self, seeker):
        return seeker.meet(self.cur_x, self.cur_y)