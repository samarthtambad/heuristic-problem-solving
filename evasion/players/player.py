#!/usr/bin/python3

import sys
import math
import copy
import socket
import random
import numpy as np
from numpy.linalg import norm
from timeit import default_timer as timer
from collections import deque
from wall import HorizontalWall, VerticalWall, DiagonalWall, CounterDiagonalWall


def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


class GameState:
    def __init__(self):
        self.playerTimeLeft = None
        self.gameNum = None
        self.tickNum = None
        self.maxWalls = None
        self.wallPlacementDelay = None
        self.boardsizeX = None
        self.boardsizeY = None
        self.currentWallTimer = None
        self.hunterXPos = None
        self.hunterYPos = None
        self.hunterXVel = None
        self.hunterYVel = None
        self.preyXPos = None
        self.preyYPos = None
        self.numWalls = None
        self.walls = None
        self.initial_state = 0
        self.prev_wall_add_tick = 0

        self.__empty_wall_positions = []

    def set(self, datastr):
        data = list(map(int, datastr.split()))
        # print(data)

        self.playerTimeLeft = data[0]
        self.gameNum = data[1]
        self.tickNum = data[2]
        self.maxWalls = data[3]
        self.wallPlacementDelay = data[4]
        self.boardsizeX = data[5]
        self.boardsizeY = data[6]
        self.currentWallTimer = data[7]
        self.hunterXPos = data[8]
        self.hunterYPos = data[9]
        self.hunterXVel = data[10]
        self.hunterYVel = data[11]
        self.preyXPos = data[12]
        self.preyYPos = data[13]
        self.numWalls = data[14]

        idx = 15
        self.walls = []
        for _ in range(self.numWalls):
            if data[idx] == 0:
                self.walls.append(HorizontalWall(data[idx+1], data[idx+2], data[idx+3]))
                idx = idx + 4
            elif data[idx] == 1:
                self.walls.append(VerticalWall(data[idx+1], data[idx+2], data[idx+3]))
                idx = idx + 4
            elif data[idx] == 2:
                self.walls.append(DiagonalWall(data[idx+1], data[idx+2], data[idx+3], data[idx+4], data[idx+5]))
                idx = idx + 6
            else:
                self.walls.append(CounterDiagonalWall(data[idx+1], data[idx+2], data[idx+3], data[idx+4], data[idx+5]))
                idx = idx + 6

    def print(self):
        print("""
              playerTimeLeft: {0}
              gameNum: {1}
              tickNum: {2}
              maxWalls: {3}
              wallPlacementDelay: {4}
              boardsizeX: {5}
              boardsizeY: {6}
              currentWallTimer: {7}
              hunterXPos: {8}
              hunterYPos: {9}
              hunterXVel: {10}
              hunterYVel: {11}
              preyXPos: {12}
              preyYPos: {13}
              numWalls: {14}
              walls: {15}
              """.format(
            self.playerTimeLeft, self.gameNum, self.tickNum, self.maxWalls, self.wallPlacementDelay, self.boardsizeX,
            self.boardsizeY, self.currentWallTimer, self.hunterXPos, self.hunterYPos, self.hunterXVel, self.hunterYVel,
            self.preyXPos, self.preyYPos, self.numWalls, self.walls))


class EvasionGame:
    def __init__(self, host: str, port: int):
        self.is_over = False
        self.is_hunter = False
        self.state = GameState()

        # make socket connection
        self.sock_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_conn.connect((host, port))

    def over(self):
        return self.is_over

    def end(self):
        self.sock_conn.close()

    def update(self):
        data = self.sock_conn.recv(4096).decode('utf-8').strip()
        print(data)

        to_send = None
        if data == "done":
            self.is_over = True
        elif data == "hunter":
            self.is_hunter = True
        elif data == "prey":
            self.is_hunter = False
        elif data == "sendname":
            to_send = "remember_the_name"
        else:
            self.state.set(data)
            self.state.print()
            to_send = self.move()

        if to_send is not None:
            print("sending: {0} \n".format(to_send))
            self.sock_conn.sendall("{0} \n".format(to_send).encode('utf-8'))

    def bounded_area_and_prey_reachable(self, hunterX, hunterY, preyX, preyY, walls):
        visited = set()
        q = deque()
        q.append((hunterX, hunterY))
        visited.add((hunterX, hunterY))
        prey_reachable = False

        while q:
            size = len(q)
            for _ in range(size):
                x, y = q.popleft()
                if x == preyX and y == preyY:
                    prey_reachable = True
                for i, j in [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]:
                    x_new, y_new = x + i, y + j
                    if x_new < 0 or x_new >= 300 or y_new < 0 or y_new >= 300:
                        continue
                    if (x_new, y_new) not in visited and not any(wall.occupies(x_new, y_new) for wall in walls):
                        q.append((x_new, y_new))
                        visited.add((x_new, y_new))

        return len(visited), prey_reachable

    def get_wall(self, wall_type):
        x, y = self.state.hunterXPos, self.state.hunterYPos
        if wall_type == 0:
            return HorizontalWall(y, 0, 299)
        elif wall_type == 1:
            return VerticalWall(x, 0, 299)
        elif wall_type == 2:
            c = y - x
            x1, y1 = 0, 0
            x2, y2 = 0, 0
            if c > 0:
                x1, y1 = 0, c
                x2, y2 = 299-c, 299
            else:
                x1, y1 = -c, 0
                x2, y2 = 299, 299+c
            return DiagonalWall(x1, x2, y1, y2, 1)
        c = x + y
        x1, y1 = 0, 0
        x2, y2 = 0, 0
        if c <= 299:
            x1, y1 = 0, c
            x2, y2 = c, 0
        else:
            x1, y1 = 299, c-299
            x2, y2 = c-299, 299
        return CounterDiagonalWall(x1, x2, y1, y2, 1)

    def move(self):
        if self.is_hunter:
            return self.hunter_move()

        return self.prey_move()

    def hunter_move_bfs(self):
        hunterX, hunterY = self.state.hunterXPos + self.state.hunterXVel, self.state.hunterYPos + self.state.hunterYVel
        preyX, preyY = self.state.preyXPos - self.state.hunterXVel, self.state.preyYPos - self.state.hunterYVel
        dist_threshold = 4
        wall_idxs_to_delete = []

        if min(abs(hunterX - preyX), abs(hunterY - preyY)) > dist_threshold:
            return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, 0, " ".join(wall_idxs_to_delete))

        timer_start = timer()
        possible_walls = []
        if (self.state.hunterXVel, self.state.hunterYVel) in [(1, 1), (-1, -1)]:    # diagonal
            possible_walls = [0, 1, 3]
        elif (self.state.hunterXVel, self.state.hunterYVel) in [(-1, 1), (1, -1)]:  # counter-diagonal
            possible_walls = [0, 1, 2]
        elif self.state.hunterXVel == 0:    # vertical
            possible_walls = [0, 2, 3]
        else:   # horizontal
            possible_walls = [1, 2, 3]

        min_area, best_wall_type = float('inf'), -1
        for wall_type in possible_walls:
            new_wall = self.get_wall(wall_type)
            temp_walls = copy.deepcopy(self.state.walls)
            temp_walls.append(new_wall)
            area, prey_reachable = self.bounded_area_and_prey_reachable(hunterX, hunterY, preyX, preyY, temp_walls)
            if prey_reachable:
                if area < min_area:
                    min_area = area
                    best_wall_type = wall_type

        timer_end = timer()
        print("Time: {0} s".format(timer_end - timer_start))

        return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, best_wall_type, " ".join(wall_idxs_to_delete))

    def get_wall_type_to_add(self):
        preyX, preyY = self.state.preyXPos, self.state.preyYPos
        hunterX, hunterY = self.state.hunterXPos, self.state.hunterYPos
        next_hunterX, next_hunterY = self.state.hunterXPos + self.state.hunterXVel, self.state.hunterYPos + self.state.hunterYVel

        # check diag
        diag_dist = self.get_perpendicular_dist(2, hunterX, hunterY, preyX, preyY)
        diag_dist_next = self.get_perpendicular_dist(2, next_hunterX, next_hunterY, preyX, preyY)
        if diag_dist >= diag_dist_next + 1 and 3 <= diag_dist <= 5:
            return 3

        # check counter diag
        cdiag_dist = self.get_perpendicular_dist(3, hunterX, hunterY, preyX, preyY)
        cdiag_dist_next = self.get_perpendicular_dist(3, next_hunterX, next_hunterY, preyX, preyY)
        if cdiag_dist >= cdiag_dist_next + 1 and 3 <= cdiag_dist <= 5:
            return 4

        # check horizontal
        hdist = self.get_perpendicular_dist(0, hunterX, hunterY, preyX, preyY)
        hdist_next = self.get_perpendicular_dist(0, next_hunterX, next_hunterY, preyX, preyY)
        if hdist >= hdist_next + 1 and 2 <= hdist <= 4:
            return 1

        # check vertical
        vdist = self.get_perpendicular_dist(1, hunterX, hunterY, preyX, preyY)
        vdist_next = self.get_perpendicular_dist(1, next_hunterX, next_hunterY, preyX, preyY)
        if vdist >= vdist_next + 1 and 2 <= vdist <= 4:
            return 2

        return 0

    def get_extreme_points(self, wall_type, x, y):
        x1, y1 = 0, 0
        x2, y2 = 0, 0
        if wall_type == 0:
            return [[0, y], [299, y]]
        elif wall_type == 1:
            return [[x, 0], [x, 299]]
        elif wall_type == 2:
            c = y - x
            x1, y1 = 0, 0
            x2, y2 = 0, 0
            if c > 0:
                x1, y1 = 0, c
                x2, y2 = 299 - c, 299
            else:
                x1, y1 = -c, 0
                x2, y2 = 299, 299 + c
            return [[x1, y1], [x2, y2]]
        c = x + y
        x1, y1 = 0, 0
        x2, y2 = 0, 0
        if c <= 299:
            x1, y1 = 0, c
            x2, y2 = c, 0
        else:
            x1, y1 = 299, c - 299
            x2, y2 = c - 299, 299
        return [[x1, y1], [x2, y2]]

    def get_perpendicular_dist(self, wall_type, x, y, px, py):
        extreme_points = self.get_extreme_points(wall_type, x, y)
        p1 = np.array(extreme_points[0])
        p2 = np.array(extreme_points[1])
        p3 = np.array([px, py])
        return norm(np.cross(p2-p1, p1-p3))/norm(p2-p1)

    def get_walls_to_delete(self, hunterX, hunterY, preyX, preyY, walls):
        walls_touched = set()
        visited = set()
        q = deque()
        q.append((hunterX, hunterY))
        visited.add((hunterX, hunterY))
        prey_reachable = False

        while q:
            size = len(q)
            for _ in range(size):
                x, y = q.popleft()
                if x == preyX and y == preyY:
                    prey_reachable = True
                for i, j in [(1, 0), (1, 1), (1, -1), (0, 1), (0, -1), (-1, 0), (-1, 1), (-1, -1)]:
                    x_new, y_new = x + i, y + j
                    if x_new < 0 or x_new >= 300 or y_new < 0 or y_new >= 300:
                        continue
                    if (x_new, y_new) not in visited:
                        is_valid = True
                        for wall in walls:
                            if wall.occupies(x_new, y_new):
                                is_valid = False
                                walls_touched.add(wall)
                        if is_valid:
                            q.append((x_new, y_new))
                            visited.add((x_new, y_new))

        deletable_walls = []
        for i, wall in enumerate(walls):
            if wall not in walls_touched:
                deletable_walls.append(i)

        return deletable_walls, len(visited), prey_reachable

    def hunter_move_old(self):
        wall_type_to_add = self.get_wall_type_to_add()
        wall_idxs_to_delete = []
        if self.state.maxWalls >= 5:
            if len(self.state.walls) == self.state.maxWalls:
                preyX, preyY = self.state.preyXPos, self.state.preyYPos
                hunterX, hunterY = self.state.hunterXPos, self.state.hunterYPos
                temp_walls = copy.deepcopy(self.state.walls)
                wall_idxs_to_delete, area, reachable = self.get_walls_to_delete(hunterX, hunterY, preyX, preyY, temp_walls)
                if not reachable:
                    wall_idxs_to_delete = [i for i in range(len(self.state.walls))]
                if len(wall_idxs_to_delete) == 0:
                    wall_idxs_to_delete = [random.randint(0, len(self.state.walls))]
        else:
            if len(self.state.walls) == self.state.maxWalls:
                if random.randint(1, 100) <= 2:
                    wall_idxs_to_delete = [random.randint(0, len(self.state.walls))]
            else:
                if random.randint(1, 100) <= 1:
                    wall_type_to_add = random.randint(1, 4)
        return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, wall_type_to_add, " ".join(map(str, wall_idxs_to_delete)))

    def hunter_move(self):
        wall_type_to_add, wall_idxs_to_delete = 0, []
        preyX, preyY = self.state.preyXPos, self.state.preyYPos
        hunterX, hunterY = self.state.hunterXPos, self.state.hunterYPos
        distX, distY = abs(hunterX - preyX), abs(hunterY - preyY)

        # if distX
        if self.state.initial_state < 4:
            if self.state.initial_state == 0:
                if 2 <= abs(distX) <= 4:
                    wall_type_to_add = 2
                    self.state.initial_state = 1
                    self.prev_wall_add_tick = self.state.tickNum
            
            if self.state.initial_state == 1:
                if (self.state.tickNum - self.prev_wall_add_tick) >= self.state.wallPlacementDelay:
                    wall_type_to_add = 2
                    self.state.initial_state = 2
            
            if self.state.initial_state == 2:
                if self.state.hunterXVel == -1:
                    min_dist, wall_idx = float('inf'), None
                    for i, wall in enumerate(self.state.walls):
                        if type(wall) == type(VerticalWall(0, 0, 0)) and abs(hunterX - wall.x) < min_dist:
                            min_dist = abs(hunterX - wall.x)
                            wall_idx = i
                    if 2 <= min_dist <= 4 and wall_idx:
                        wall_idxs_to_delete.append(wall_idx)
                        self.state.initial_state = 3
            
            if self.state.initial_state == 3:
                if 2 <= abs(distX) <= 3:
                    wall_type_to_add = 2
                    self.state.initial_state = 4
        
        else:
            if self.state.maxWalls > 2 and len(self.state.walls) > 2:
                temp_walls = copy.deepcopy(self.state.walls)
                wall_idxs_to_delete, area, reachable = self.get_walls_to_delete(hunterX, hunterY, preyX, preyY, temp_walls)

            xdist = self.state.hunterXPos - self.state.preyXPos
            ydist = self.state.hunterYPos - self.state.preyYPos

            if self.state.hunterXVel == 0:
                wall_type_to_add = 0
            elif xdist * self.state.hunterXVel >= 0:
                wall_type_to_add = 0
            elif 2 <= abs(xdist) <= 4:
                wall_type_to_add = 2
            elif self.state.hunterYVel == 0:
                wall_type_to_add = 0
            elif ydist * self.state.hunterYVel >= 0:
                wall_type_to_add = 0
            elif 2 <= abs(ydist) <= 4:
                wall_type_to_add = 1

        return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, wall_type_to_add, " ".join(map(str, wall_idxs_to_delete)))


    def hunter_move_default(self):
        wall_type_to_add = 0
        wall_idxs_to_delete = []

        xdist = self.state.hunterXPos - self.state.preyXPos
        ydist = self.state.hunterYPos - self.state.preyYPos

        if self.state.hunterXVel == 0:
            wall_type_to_add = 0
        elif xdist * self.state.hunterXVel >= 0:
            wall_type_to_add = 0
        elif 2 <= abs(xdist) <= 4:
            wall_type_to_add = 2
        elif self.state.hunterYVel == 0:
            wall_type_to_add = 0
        elif ydist * self.state.hunterYVel >= 0:
            wall_type_to_add = 0
        elif 2 <= abs(ydist) <= 4:
            wall_type_to_add = 1
        else:
            wall_type_to_add = 0

        return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, wall_type_to_add, " ".join(wall_idxs_to_delete))

    def prey_move_random(self):
        x = random.randint(-1, 1)
        y = random.randint(-1, 1)
        return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, x, y)

    def prey_move(self):
        close_move = 12
        dx, dy = 0, 0
        if dist(self.state.preyXPos, self.state.preyYPos, self.state.hunterXPos, self.state.hunterYPos) < close_move:
            if self.state.hunterXVel == 1 and self.state.hunterYVel == -1:
                if self.state.preyXPos > self.state.hunterXPos and self.state.preyYPos < self.state.hunterYPos:
                    dx = -1 if abs(self.state.preyXPos - self.state.hunterXPos) < abs(self.state.preyYPos - self.state.hunterYPos) else 1
                    dy = -1 if abs(self.state.preyXPos - self.state.hunterXPos) < abs(self.state.preyYPos - self.state.hunterYPos) else 1
                else:
                    dx, dy = -1, 1
            elif self.state.hunterXVel == 1 and self.state.hunterYVel == 1:
                if self.state.preyXPos > self.state.hunterXPos and self.state.preyYPos > self.state.hunterYPos:
                    dx = -1 if abs(self.state.preyXPos - self.state.hunterXPos) < abs(self.state.preyYPos - self.state.hunterYPos) else 1
                    dy = 1 if abs(self.state.preyXPos - self.state.hunterXPos) < abs(self.state.preyYPos - self.state.hunterYPos) else -1
                else:
                    dx, dy = -1, -1
            elif self.state.hunterXVel == -1 and self.state.hunterYVel == 1:
                if self.state.preyXPos < self.state.hunterXPos and self.state.preyYPos > self.state.hunterYPos:
                    dx = -1 if abs(self.state.preyXPos - self.state.hunterXPos) > abs(self.state.preyYPos - self.state.hunterYPos) else 1
                    dy = -1 if abs(self.state.preyXPos - self.state.hunterXPos) > abs(self.state.preyYPos - self.state.hunterYPos) else 1
                else:
                    dx, dy = 1, -1
            elif self.state.hunterXVel == -1 and self.state.hunterYVel == -1:
                if self.state.preyXPos < self.state.hunterXPos and self.state.preyYPos < self.state.hunterYPos:
                    dx = -1 if abs(self.state.preyXPos - self.state.hunterXPos) > abs(self.state.preyYPos - self.state.hunterYPos) else 1
                    dy = 1 if abs(self.state.preyXPos - self.state.hunterXPos) > abs(self.state.preyYPos - self.state.hunterYPos) else -1
                else:
                    dx, dy = 1, 1
        else:
            dx = -1 if self.state.preyXPos > self.state.hunterXPos else 1
            dy = -1 if self.state.preyYPos > self.state.hunterYPos else 1

        return "{0} {1} {2} {3}".format(self.state.gameNum, self.state.tickNum, dx, dy)


if __name__ == "__main__":
    host = "localhost"
    port = int(sys.argv[1])

    game = EvasionGame(host, port)
    while not game.over():
        game.update()
    game.end()
