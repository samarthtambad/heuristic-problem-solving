# -*- coding: utf-8 -*-
"""This file contains the socket server used for the Expanding Nim game.

It is a very simple implementation that has methods to wait for a player to
move, update all players after each move, and establish connections.

@author: Munir Contractor <mmc691@nyu.edu>
"""

import socket


class Server():
    """The socket server that maintains communication with the players"""

    DATA_SIZE = 1024

    def __init__(self, host, port):
        """
        Args:
            **host:** Host for the server\n
            **port:** Port to run the server on\n
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.player_sockets = [None, None]
        self.socket.listen(2)

    def establish_connections(self):
        """Establishes connection with the players"""
        self.player_sockets[0], _ = self.socket.accept()
        self.player_sockets[1], _ = self.socket.accept()
        return [self.receive(0), self.receive(1)]

    def update_all_clients(self, data):
        """Updates all players by sending the data to the client sockets"""
        for sck in self.player_sockets:
            sck.sendall(data)

    def receive(self, player):
        """Receives a move from the specified player"""
        return self.player_sockets[player].recv(self.DATA_SIZE)

    def close(self):
        """Close the server"""
        self.socket.close()

    def __del__(self):
        self.close()
