# -*- coding: utf-8 -*-
"""This file contains the client class used by the Expanding Nim game

This class can either be instantiated and used in Python or controlled
via the command line.

@author: Munir Contractor <mmc691@nyu.edu>
"""

import json
import socket


class Client():
    """The client class for the Expanding Nim game"""

    DATA_SIZE = 1024

    def __init__(self, name, goes_first, server_address):
        """
        Args:
            **name:** The name you want to give your player\n
            **goes_first:** Boolean indicator whether you take the first move
            or not\n
            **server_address:** A tuple of the form (address, port) of the
            server
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(server_address)
        self.__order = 0 if goes_first else 1
        self.__send_json({'name': name, 'order': self.__order})
        init_status = self.receive_move()
        self.init_stones = init_status['init_stones']
        self.init_resets = init_status['init_resets']

    def close(self):
        self.socket.close()

    def __del__(self):
        self.close()

    def __send_json(self, json_object):
        """Helper method to send an object to the server as JSON"""
        self.socket.sendall(bytes(json.dumps(json_object), 'utf-8'))

    def make_move(self, num_stones, reset=False):
        """Sends your move to the server and waits for the opponent to move

        The return value is dict containing the keys as follows:
            ``finished``: Boolean indicator whether the game is over or not\n
            ``stones_left``: Stones left in the game\n
            ``current_max``: New current max value\n
            ``reset_used``: Boolean indicator (should be same as input)\n
            ``stones_removed``: Number of stones removed (should match
            the input)\n
        If  the ``finished`` indicator evaluates to ``True``, two extra keys,
        ``winner`` and ``reason`` will be included to indicate the winning
        player and the reason for the win.

        Args:
            **num_stones:** The number of stones to remove.\n
            **reset:** Boolean indicator whether you want to use reset or not.

        Return:
            A dict containing the keys described above
        """
        self.__send_json({'order': self.__order, 'num_stones': num_stones,
                          'reset': reset})
        return self.receive_move()

    def receive_move(self):
        """Receives a move and the state of the game after the move

        The return value is dict containing the keys as follows:
            ``finished``: Boolean indicator whether the game is over or not\n
            ``stones_left``: Stones left in the game\n
            ``current_max``: New current max value\n
            ``reset_used``: Boolean indicator whether reset was used in the
            move\n
            ``stones_removed``: Number of stones removed in the move\n
        If  the ``finished`` indicator evaluates to ``True``, two extra keys,
        ``winner`` and ``reason`` will be included to indicate the winning
        player and the reason for the win.

        Return:
            A dict containing the keys described above
        """
        return json.loads(self.socket.recv(self.DATA_SIZE).decode('utf-8'))

    def __read_move(self):
        try:
            move = input('Please enter your move: ').split(' ')
            return int(move[0]), bool(int(move[1]))
        except Exception:
            print('Invalid move string')
            return self.__read_move()

    def send_move(self):
        """Reads a move from stdin and sends it to the server

        The move has to be in the form '%d %d' where the first number
        is the number of stones to remove and second number is a boolean
        flag for whether reset should be done. The move and the result
        are printed out.
        """
        move = self.__read_move()
        status = self.make_move(move[0], move[1])
        print('You took %d stones%s' % (move[0],
              ' and used reset.' if move[1] else '.'))
        print('Current max: %d' % status['current_max'])
        print('Stones left: %d' % status['stones_left'])
        print('---------------------------------------')
        if status['finished']:
            print('Game over\n%s' % status['reason'])
            exit(0)

    def get_move(self):
        """Gets the move made by the opponent and prints it out"""
        status = self.receive_move()
        print('Opponent took %d stones%s' % (status['stones_removed'],
              ' and used reset.' if status['reset_used'] else '.'))
        print('Current max: %d' % status['current_max'])
        print('Stones left: %d' % status['stones_left'])
        print('---------------------------------------')
        if status['finished']:
            print('Game over\n%s' % status['reason'])
            exit(0)
