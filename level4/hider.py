from defines import Config
from player import Player
from queue import Queue
import heapq
import copy
import random


class Hider(Player):
    def __init__(self, map, n, m, obs_range, init_pos, seeker_init_pos, obs, obs_sign_to_hider, obs_need, hide_place,
                 hider_status, obs_to_cell, is_generate_path, id):
        super().__init__(map, n, m, obs_range, init_pos, obs)
        self.__seeker_init_pos = seeker_init_pos
        self.__cur_dest = init_pos
        self.cur_x, self.cur_y = init_pos
        self.__cur_step = None
        self.__init_seeker_heuristic_map()
        self.__approximate_seeker_delay = 30
        self.is_regconized = False
        self.seeker_coord = None
        self.__prev_cur_dest = None
        # self.__update_destination()
        self.obs_list = []  # list of current observable cells
        self.prepare_path = None  # store moving path in pre-game session
        self.pregame_should_move = True
        self.finish_prepare = False
        #        self.__navigate()
        self.BFS_map = self.BFS_full_map()
        self.init_heuristic_map()
        self.obs_sign_to_hider = obs_sign_to_hider
        self.obs_need = obs_need
        self.hide_place = hide_place
        self.hider_status = hider_status
        self.obs_to_cell = obs_to_cell
        self.is_generate_path = is_generate_path
        self.id = id
        self.__cur_path = []

    def update_seeker_pos(self, x, y):
        self.__seeker_init_pos = x, y

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

    def should_announced(self, turn):
        return turn > Config.PREGAME_TURN and turn % 5 == 0

    def __update_destination(self):
        self.__cur_dest = self.__find_dest((self.cur_x, self.cur_y))
        self.__cur_step = 0

    def __should_stay(self, turn):
        if turn < self.__BFS_seeker_map[self.cur_x][self.cur_y] + self.__approximate_seeker_delay:
            return True
        if self.hmap[self.cur_x][self.cur_y] > 2:
            return True
        return False

    def __run(self):
        self.__init_seeker_heuristic_map()
        self.__update_destination()

    def check_for_seeker(self):
        for i in range(self.cur_x - self.obs_range, self.cur_x + self.obs_range + 1):
            for j in range(self.cur_y - self.obs_range, self.cur_y + self.obs_range + 1):
                if i >= 0 and i < self.n and j >= 0 and j < self.m and self.is_observable(i, j) and self.map[i][
                    j] == Config.SEEKER:
                    self.is_regconized, self.seeker_coord = True, (i, j)
                    return
        self.is_regconized, self.seeker_coord = False, None

    def make_a_move(self, dxy):
        dx, dy = dxy

        dir_x, dir_y = dx - self.cur_x, dy - self.cur_y
        if len(self.obs_need) > 0 and self.id in self.obs_sign_to_hider and self.is_bring_obs(self.obs_need[0]):
            obs_id = self.obs_need[0]
            for i in range(len(self.obs[obs_id])):
                self.obs[obs_id][i] = self.obs[obs_id][i][0] + dir_x, self.obs[obs_id][i][1] + dir_y

        self.cur_x, self.cur_y = dx, dy
        self.__cur_dest = (self.cur_x, self.cur_y)
        self.__update_observable_range()
        self.update_obs_loc()
        return dir_x, dir_y

    def BFS_full_map(self):
        res = [[-1] * self.m for _ in range(self.n)]

        q = Queue()
        q.put((self.cur_x, self.cur_y))
        res[self.cur_x][self.cur_y] = 0

        while not q.empty():
            cx, cy = q.get_nowait()
            cur_dist = res[cx][cy]

            for dx, dy in Config.DIR:
                nx, ny = cx + dx, cy + dy
                if self.isAccessable(nx, ny) and res[nx][ny] == -1:
                    q.put((nx, ny))
                    res[nx][ny] = cur_dist + 1
        return res

    def seeker_is_reachable(self):
        x, y = self.__seeker_init_pos
        return self.BFS_map[x][y] != -1

    def choose_nearest_obstacle(self):
        id = x = y = None
        distance = Config.IMPOSSIBLE
        for i in range(len(self.obs)):
            for j in range(len(self.obs[i])):
                cx, cy = self.obs[i][j]
                if self.BFS_map[cx][cy] < distance:
                    distance = self.BFS_map[cx][cy]
                    id = i
                    x, y = cx, cy
        return id, distance, x, y

    def should_move(self, distance, x, y):
        return self.is_pregame(distance + self.__BFS_seeker_map[x][y])

    def generate_path(self):
        # TODO: self.prepare_path contains list of (dx, dy) towards self.obs[self.obs_id]
        # e.g. self.prepare_path = [(0, 1), (0, 1)]
        if self.obs_sign_to_hider[0] is None or not self.hider_status[self.obs_sign_to_hider[0]]:
            self.obs_sign_to_hider[0] = self.id
            # print("finish first step")

        if len(self.obs_need) > 0:
            if self.id in self.obs_sign_to_hider:
                # print("go to first if")
                self.prepare_path = self.find_way_push_obs_to_this_cell(self.obs_need[0], self.obs_to_cell[0][0],
                                                                        self.obs_to_cell[0][1])
                return

        self.prepare_path = self.__find_path((self.cur_x, self.cur_y), (self.hide_place[0], self.hide_place[1]))

    def push_toward_seeker(self):
        # TODO: push the nearby obstacle towards the seeker
        return self.make_a_move((0, 0))

    def update_obs_loc(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.map[i][j] == Config.OBS:
                    self.map[i][j] = Config.EMPTY
        for obstacle in self.obs:
            for x, y in obstacle:
                # print("err", x, y, obstacle)
                self.map[x][y] = Config.OBS

    def prepare(self):
        if not self.seeker_is_reachable():
            return self.make_a_move((0, 0))

        ux, uy = self.cur_x, self.cur_y

        if not self.is_generate_path[0]:
            self.is_generate_path[0] = True
            self.generate_the_way_to_win()

        if self.prepare_path is None or (len(self.obs_need) > 0 and (self.obs_sign_to_hider[0] is None or not self.hider_status[self.obs_sign_to_hider[0]])):
            self.generate_path()

        if self.prepare_path is not None and len(self.prepare_path) > 0:
            ux, uy = self.prepare_path.pop(0)

        if not self.isAccessable(ux, uy):
            self.generate_path()

        if self.obs_sign_to_hider[0] == self.id:
            if len(self.obs_need) > 0 and self.obs[self.obs_need[0]][0] == (
                    self.obs_to_cell[0][0], self.obs_to_cell[0][1]):
                self.obs_need.remove(self.obs_need[0])
                self.obs_to_cell.remove(self.obs_to_cell[0])
                self.prepare_path = None

        return self.make_a_move((ux, uy))

    # return id of nearest horizontal obs and path to cell (x, y)
    def find_horizontal_obs_to_this_cell_except_this_obs(self, x, y, exc):
        best_path = None
        id_best_path = None
        for obs_id in range(len(self.obs)):
            if obs_id == exc:
                continue
            if self.obs[obs_id][0][0] == self.obs[obs_id][1][0]:  # horizontal obs
                new_path = self.can_obs_go_to_this_location(obs_id, x, y)
                if new_path is None:
                    continue
                if best_path is None or len(best_path) > len(new_path):
                    best_path = new_path
                    id_best_path = obs_id
        return id_best_path, best_path

    # return id of nearest vertical obs and path to cell (x, y)
    def find_vertical_obs_to_this_cell_except_this_obs(self, x, y, exc):
        best_path = None
        id_best_path = None
        for obs_id in range(len(self.obs)):
            if obs_id == exc:
                continue
            if self.obs[obs_id][0][1] == self.obs[obs_id][1][1]:  # vertical obs
                new_path = self.can_obs_go_to_this_location(obs_id, x, y)
                if new_path is None:
                    continue
                if best_path is None or len(best_path) > len(new_path):
                    best_path = new_path
                    id_best_path = obs_id
        return id_best_path, best_path

    def can_obs_and_hider_go_to_this_location(self, obs_id, cur_x, cur_y, u, v):  # return None if cannot : path
        path = [[(-1, -1)] * self.m for _ in range(self.n)]
        q = Queue()
        visited = [[False] * self.m for _ in range(self.n)]
        visited[cur_x][cur_y] = True
        q.put((cur_x, cur_y))
        while not q.empty():
            x, y = q.get()
            for dx, dy in Config.DIR:
                ux, uy = x + dx, y + dy
                if self.isAccessable(ux, uy) and not visited[ux][uy] \
                        and self.isAccessable(ux + self.obs[obs_id][0][0] - cur_x,
                                              uy + self.obs[obs_id][0][1] - cur_y) \
                        and self.isAccessable(ux + self.obs[obs_id][1][0] - cur_x,
                                              uy + self.obs[obs_id][1][1] - cur_y):
                    visited[ux][uy] = True
                    q.put((ux, uy))
                    path[ux][uy] = x, y

                    if (ux + self.obs[obs_id][0][0] - cur_x, uy + self.obs[obs_id][0][1] - cur_y) == (u, v):

                        # print("hello")
                        temp_path = []
                        x, y = ux, uy
                        while path[x][y] != (cur_x, cur_y):
                            if path[x][y] == (-1, -1):
                                print("wao")
                                exit(0)
                            temp_path.append(path[x][y])
                            x, y = path[x][y]
                        temp_path.reverse()
                        temp_path.append((ux, uy))
                        return temp_path
        return None

    def can_obs_go_to_this_location(self, obs_id, u, v):  # return None if cannot : path
        path = [[(-1, -1)] * self.m for _ in range(self.n)]
        q = Queue()
        visited = [[False] * self.m for _ in range(self.n)]
        visited[self.obs[obs_id][0][0]][self.obs[obs_id][0][1]] = True
        q.put((self.obs[obs_id][0][0], self.obs[obs_id][0][1]))
        while not q.empty():
            x, y = q.get()
            for dx, dy in Config.DIR:
                ux, uy = x + dx, y + dy
                if self.isAccessable(ux, uy) and not visited[ux][uy] \
                        and self.isAccessable(ux + self.obs[obs_id][1][0] - self.obs[obs_id][0][0],
                                              uy + self.obs[obs_id][1][1] - self.obs[obs_id][0][1]):
                    visited[ux][uy] = True
                    q.put((ux, uy))
                    path[ux][uy] = x, y

                    if (ux, uy) == (u, v):

                        # print("hello")
                        temp_path = []
                        x, y = ux, uy
                        while path[x][y] != (self.obs[obs_id][0][0], self.obs[obs_id][0][1]):
                            if path[x][y] == (-1, -1):
                                print("wao")
                                exit(0)
                            temp_path.append(path[x][y])
                            x, y = path[x][y]
                        temp_path.reverse()
                        temp_path.append((ux, uy))
                        return temp_path
        return None

    def is_bring_obs(self, obs_id):
        for obs in self.obs[obs_id]:
            dx, dy = obs[0] - self.cur_x, obs[1] - self.cur_y
            if dx * dx + dy * dy == 1:
                return True
        return False

    def find_way_push_obs_to_this_cell(self, obs_id, u, v):
        path = None
        for cell in self.obs[obs_id]:
            # print("cell:", cell)
            for dx, dy in Config.DIR:
                if (dx * dx + dy * dy) == 1 and self.isAccessable(cell[0] + dx, cell[1] + dy):
                    # print("begin find way from ", self.cur_x, self.cur_y, " to ", cell[0] + dx, cell[0] + dy)
                    path1 = self.__find_path((self.cur_x, self.cur_y), (cell[0] + dx, cell[1] + dy))
                    # print("finish")
                    # print("begin 284")
                    path2 = self.can_obs_and_hider_go_to_this_location(obs_id, cell[0] + dx, cell[1] + dy, u, v)
                    # print("finish")

                    if path1 is None or path2 is None:
                        continue

                    for i in path2:
                        path1.append(i)

                    if path is None or len(path1) < len(path):
                        path = path1
        return path

    def is_this_hider_still_alive(self, hider_id):
        return self.hider_status[hider_id]

    # None | cell, list_obs, obs_dest, cost
    def can_this_cell_be_place_for_hider_to_hide_and_place_obs_around(self, x, y):
        # if x == 4 and y == 11:
        #     return (4, 11), [1, 0], [[3, 10], [3, 9]], 10
        # return None

        id_ver, path_ver = None, None
        id_hor, path_hor = None, None
        des_ver, des_hor = None, None

        if not self.isAccessable(x - 1, y - 1) and not self.isAccessable(x - 1, y) and not self.isAccessable(x, y - 1) \
                and not self.isAccessable(x - 1, y + 1) and not self.isAccessable(x + 1, y - 1):
            if not self.isAccessable(x + 2, y - 1):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x, y + 1, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x + 2, y, None)
                des_ver = [x, y + 1]
                des_hor = [x + 2, y]
            elif not self.isAccessable(x - 1, y + 2):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x, y + 2, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x + 1, y, None)
                des_ver = [x, y + 2]
                des_hor = [x + 1, y]

        if not self.isAccessable(x - 1, y + 1) and not self.isAccessable(x - 1, y) and not self.isAccessable(x, y - 1) \
                and not self.isAccessable(x + 1, y + 1) and not self.isAccessable(x - 1, y - 1):
            if not self.isAccessable(x - 1, y - 2):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x, y - 2, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x + 1, y - 1, None)
                des_ver = [x, y - 2]
                des_hor = [x + 1, y - 1]
            elif not self.isAccessable(x - 1, y + 2):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x, y - 1, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x + 2, y - 1, None)
                des_ver = [x, y - 1]
                des_hor = [x + 2, y - 1]

        if not self.isAccessable(x + 1, y + 1) and not self.isAccessable(x, y + 1) and not self.isAccessable(x + 1, y) \
                and not self.isAccessable(x - 1, y + 1) and not self.isAccessable(x + 1, y - 1):
            if not self.isAccessable(x - 2, y + 1):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x - 1, y - 1, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x - 2, y - 1, None)
                des_ver = [x - 1, y - 1]
                des_hor = [x - 2, y - 1]
            elif not self.isAccessable(x + 1, y - 2):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x - 1, y - 2, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x - 1, y - 1, None)
                des_ver = [x - 1, y - 2]
                des_hor = [x - 2, y - 1]

        if not self.isAccessable(x + 1, y - 1) and not self.isAccessable(x, y - 1) and not self.isAccessable(x + 1, y) \
                and not self.isAccessable(x + 1, y + 1) and not self.isAccessable(x - 1, y - 1):
            if not self.isAccessable(x - 2, y - 1):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x - 1, y + 1, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x - 2, y, None)
                des_ver = [x - 1, y + 1]
                des_hor = [x - 2, y]
            elif not self.isAccessable(x + 1, y + 2):
                id_ver, path_ver = self.find_vertical_obs_to_this_cell_except_this_obs(x - 1, y + 2, None)
                id_hor, path_hor = self.find_horizontal_obs_to_this_cell_except_this_obs(x - 1, y, None)
                des_ver = [x - 1, y + 1]
                des_hor = [x - 1, y]

        if id_ver is None or id_hor is None:
            return None

        return (x, y), [id_ver, id_hor], [des_ver, des_hor], len(path_ver) + len(path_hor)

    def generate_the_way_to_win(self):
        # TODO: self.prepare_path contains list of (dx, dy) towards self.obs[self.obs_id]
        # e.g. self.prepare_path = [(0, 1), (0, 1)]

        best_cell, best_list_obs, best_obs_dest, best_cost = None, None, None, None
        for i in range(self.n):
            for j in range(self.m):
                tmp = self.can_this_cell_be_place_for_hider_to_hide_and_place_obs_around(i, j)
                if tmp is None:
                    continue
                cell, list_obs, obs_dest, cost = tmp
                if best_list_obs is None or cost > best_cost:
                    best_cell = cell
                    best_list_obs = list_obs
                    best_obs_dest = obs_dest
                    best_cost = cost

        for obs_id in best_list_obs:
            self.obs_need.append(obs_id)
        for loc in best_obs_dest:
            self.obs_to_cell.append(loc)
        self.hide_place[0], self.hide_place[1] = best_cell[0], best_cell[1]

    def move(self, turn):
        # TODO: uncomment the next two lines to test
        return self.prepare()
        self.check_for_seeker()

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
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def __heuristic_value(self, src, i, j):
        k_h = 20
        k_m = 10
        k_s = 1
        res = 0
        if (self.is_regconized == True):
            k_h = 0
            k_m = 5
            k_s = 15
            res += 50 * self.__mahattan_distance(src, self.seeker_coord)
        return res + k_h * self.hmap[i][j] - k_m * self.__mahattan_distance(src, (i, j)) + k_s * \
               self.__BFS_seeker_map[i][j]

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
                if i != self.cur_x and j != self.cur_y and (i, j) != self.__prev_cur_dest and self.isAccessable(i, j):
                    heapq.heappush(dest, DestEntry((i, j), self.__heuristic_value(src, i, j)))

        while len(dest) != 0:
            des = heapq.heappop(dest).pos
            temp_path = self.__find_path(src, des)
            print("{} {} {}".format(src, des, temp_path))
            if temp_path != None:
                self.__cur_path = temp_path
                return des

    def isAccessable(self, x, y):
        if x < 0 or x >= self.n:
            return False
        if y < 0 or y >= self.m:
            return False
        if self.map[x][y] in [Config.WALL, Config.OBS]:  # TODO: remove HIDER when gui fixed
            return False
        return True

    def __BFS(self, src, des):
        path = [[(-1, -1)] * self.m for _ in range(self.n)]
        q = Queue()
        visited = [[False] * self.m for _ in range(self.n)]
        x, y = src
        visited[x][y] = True
        q.put((x, y))
        path[x][y] = (x, y)
        while not q.empty():
            x, y = q.get()

            if (x, y) == des:
                return path

            for dx, dy in Config.DIR:
                ux, uy = x + dx, y + dy
                if self.isAccessable(ux, uy) and not visited[ux][uy]:
                    visited[ux][uy] = True
                    q.put((ux, uy))
                    path[ux][uy] = x, y
        return None

    def __find_path(self, src, des):
        temp_path = []
        BFS_path = self.__BFS(src, des)
        x, y = des
        if BFS_path != None:
            while BFS_path[x][y] != src:
                if BFS_path[x][y] == (-1, -1):
                    raise Exception("bug find path")
                    exit(0)
                temp_path.append(BFS_path[x][y])
                x, y = BFS_path[x][y]
            temp_path.reverse()
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
