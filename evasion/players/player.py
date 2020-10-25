#!/usr/bin/python3

import socket
import random
import sys
import time
import random


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

    def set(self, datastr):
        data = list(map(int, datastr.split()))
        print(data)

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
        for _ in range(self.numWalls):
            if idx == 0 or idx == 1:
                self.walls.append(data[idx:idx+4])
                idx = idx + 4
            else:
                self.walls.append(data[idx:idx+5])
                idx = idx + 5

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
              hunterYVel: {11]
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
            # self.state.print()
            to_send = self.move()

        if to_send is not None:
            print("sending: {0} \n".format(to_send))
            self.sock_conn.sendall("{0} \n".format(to_send).encode('utf-8'))

    def move(self):
        if self.is_hunter:
            return self.hunter_move()

        return self.prey_move()

    def hunter_move(self):
        return "hunter_move"

    def prey_move(self):
        return "prey_move"


if __name__ == "__main__":
    host = "localhost"
    port = int(sys.argv[1])

    game = EvasionGame(host, port)
    while not game.over():
        game.update()
    game.end()
