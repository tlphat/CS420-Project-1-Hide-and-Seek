from defines import Config
from player import Player
from queue import Queue
import heapq
import copy
import random

class Hider(Player):
    def __init__(self, map, n, m, obs_range, init_pos, seeker_init_pos, obs):
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
        self.obs_list = [] # list of current observable cells
        self.prepare_path = [] # store moving path in pre-game session
        self.pregame_should_move = True
        self.finish_prepare = False
#        self.__navigate()
        self.BFS_map = self.BFS_full_map()
        self.init_heuristic_map()

    def update_seeker_pos(self, x, y):
        self.__seeker_init_pos = x,y

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
                if i >= 0 and i < self.n and j >= 0 and j < self.m and self.is_observable(i, j) and self.map[i][j] == Config.SEEKER:
                    self.is_regconized, self.seeker_coord = True, (i, j)
                    return
        self.is_regconized, self.seeker_coord = False, None

    def make_a_move(self, dxy):
        dx, dy = dxy
        self.cur_x, self.cur_y = self.cur_x + dx, self.cur_y + dy
        self.__cur_dest = (self.cur_x, self.cur_y)
        self.__update_observable_range()
        return dxy

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
        pass

    def push_toward_seeker(self):
        # TODO: push the nearby obstacle towards the seeker
        return self.make_a_move((0, 0))
    
    def is_obs_blocked_up(self, obs_id):
        i, j = 0
        while j < len(self.obs_list[obs_id]) and self.obs_list[obs_id][j][0] == self.obs_list[obs_id][i][0]: # cell of obs in same row
            if self.isAccessable(self.obs_list[obs_id][j][0] - 1, self.obs_list[obs_id][j][1]):
                return False
            j += 1
        return True
            
    def is_obs_blocked_down(self, obs_id):
        i, j = 0
        while j < len(self.obs_list[obs_id]) and self.obs_list[obs_id][j][0] == self.obs_list[obs_id][i][0]: # cell of obs in same row
            if self.isAccessable(self.obs_list[obs_id][j][0] + 1, self.obs_list[obs_id][j][1]):
                return False
            j += 1
        return True
            
    def is_obs_blocked_left(self, obs_id):
        i, j = 0
        
        while j < len(self.obs_list[obs_id]) and self.obs_list[obs_id][j][0] == self.obs_list[obs_id][i][0]: # cell of obs in same row
            if self.isAccessable(self.obs_list[obs_id][j][0] - 1, self.obs_list[obs_id][j][1]):
                return False
            j += 1
        return True
            
    def is_obs_blocked_right(self, obs_id):
        i, j = 0
        while j < len(self.obs_list[obs_id]) and self.obs_list[obs_id][j][0] == self.obs_list[obs_id][i][0]: # cell of obs in same row
            if self.isAccessable(self.obs_list[obs_id][j][0] - 1, self.obs_list[obs_id][j][1]):
                return False
            j += 1
        return True

    def make_all_obs_become_wall_if_can(self):

    def find_horizontal_obs_to_this_cell(self, x, y): # return id of nearist horizontal obs and path to cell (x, y)
        best_path = None
        id_best_path = None
        for obs_id in range(len(self.obs_list)):
            if self.obs_list[obs_id][0][0] == self.obs_list[obs_id][1][0]: # horizontal obs
                new_path = self.can_obs_go_to_this_location(obs_id, x, y)
                if new_path == None:
                    continue
                if best_path == None or len(best_path) > len(new_path):
                    best_path = new_path
                    id_best_path = obs_id
        return id_best_path, best_path

    def find_vertical_obs_to_this_cell(self, x, y): # return id of nearist vertical obs and path to cell (x, y)
        best_path = None
        id_best_path = None
        for obs_id in range(len(self.obs_list)):
            if self.obs_list[obs_id][0][1] == self.obs_list[obs_id][1][1]: # vertical obs
                new_path = self.can_obs_go_to_this_location(obs_id, x, y)
                if new_path == None:
                    continue
                if best_path == None or len(best_path) > len(new_path):
                    best_path = new_path
                    id_best_path = obs_id
        return id_best_path, best_path

    def can_obs_go_to_this_location(self, obs_id, x, y): # return None if cannot : path 
        path = [[(-1, -1)] * self.m for _ in range(self.n)]
        q = Queue()
        visited = [[False] * self.m for _ in range(self.n)]
        visited[self.obs_list[obs_id][0]][self.obs_list[obs_id][1]] = True
        q.put(self.obs_list[obs_id])
        while not q.empty():
            x, y = q.get()
            for dx, dy in Config.DIR:
                ux, uy = x + dx, y + dy
                if not visited[ux][uy]:
                    check = True
                    for cell in self.obs_list[obs_id]:
                        if not self.isAccessable(ux - self.obs_list[obs_id][0] + cell[0], uy - self.obs_list[obs_id][1] + cell[1]): # need to check this
                            check = False
                            break
                    
                    if not check:
                        continue

                    visited[ux][uy] = True
                    q.put((ux, uy))
                    path[ux][uy] = x, y
                if (ux, uy) == (x, y):
                    return path
        return None
    
    def can_this_cell_be_place_for_hider_to_hide_and_place_obs_around(self, x, y):
        n
        for dx, dy in Config.DIR:
            if not self.isAccessable(x + dx, y + dy):
                check = True
                break
        
        if not Check:
            return None

    def prepare(self):
        if not self.seeker_is_reachable():
            return self.make_a_move((0, 0))

        # maybe prepare time is over but its still time to lock down hider
        # go towards obstacle
        # if not self.pregame_should_move: # don't have enough time to setup
        #     return self.make_a_move((0, 0))

        # if len(self.prepare_path) == 0: # have not decided yet
        #     if self.finish_prepare: # has come to the obstacle position
        #         return self.push_toward_seeker()

        #     self.obs_id, distance, x, y = self.choose_nearest_obstacle()
        #     if not self.should_move(distance, x, y): # too far to reach
        #         self.pregame_should_move = False
        #         return self.make_a_move((0, 0))

        #     self.finish_prepare = True
        #     self.generate_path()

        # if len(self.prepare_path) != 0:
        #     return self.make_a_move(self.prepare_path.pop(0))
        # return self.make_a_move((0, 0))

    def move(self, turn):
        # TODO: uncomment the next two lines to test
        # if self.is_pregame(turn):
        #     return self.prepare()
        self.check_for_seeker()
        if self.is_regconized:
            self.__run()
            if turn % 2 != 0:
                return (0, 0)
        if self.__cur_dest == (self.cur_x, self.cur_y):
            if self.__should_stay(turn) == True: 
                return (0, 0)
            self.__prev_cur_dest = self.__cur_dest
            self.__update_destination()
        x, y = self.__cur_path[self.__cur_step]
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
        k_h = 20
        k_m = 10
        k_s = 1
        res = 0
        if (self.is_regconized == True):
            k_h = 0
            k_m = 5
            k_s = 15
            res += 50 * self.__mahattan_distance(src, self.seeker_coord)
        return res + k_h * self.hmap[i][j] - k_m * self.__mahattan_distance(src, (i,j)) + k_s * self.__BFS_seeker_map[i][j]

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
        if self.map[x][y] in [Config.WALL, Config.OBS]: #TODO: remove HIDER when gui fixed
            return False
        return True

    def __BFS(self, src, des):
        path = [[(-1, -1)] * self.m for _ in range(self.n)]
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
                    return path
        return None

    def __find_path(self, src, des):
        temp_path = []
        BFS_path = self.__BFS(src, des)
        x,y = des
        if BFS_path != None:
            while BFS_path[x][y] != src:
                if (BFS_path[x][y] == (-1, -1)):
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