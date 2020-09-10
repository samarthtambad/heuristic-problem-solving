#!/usr/bin/python3
# -*- coding: utf-8 -*-

import atexit

from client import Client


def check_game_status(game_state):
    if game_state['finished']:
        print(game_state['reason'])
        exit(0)


def my_algo(game_state):
    """This function contains your algorithm for the game"""
    return 3, False


if __name__ == '__main__':
    # Read these from stdin to make life easier
    goes_first = True
    ip = '127.0.0.1'
    port = 9000

    client = Client('my name', goes_first, (ip, port))
    atexit.register(client.close)
    stones = client.init_stones
    resets = client.init_resets

    if goes_first:
        num_stones, reset = my_algo(None)
        check_game_status(client.make_move(num_stones, reset))
    while True:
        game_state = client.receive_move()
        check_game_status(game_state)
        # Some parsing logic to convert game state to algo_inputs
        num_stones, reset = my_algo(game_state)
        check_game_status(client.make_move(num_stones, reset))
