#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Script to start the Expanding Nim game

To start the game, run this script with the following options:
    ./start-game.py [-m <max>|-a <address>|-p <port>|-t <secs>] n r
where:
    n is the number of stones to start game with
    r is the number of resets available to the players
    m is the initial maximum number (Default: 3)
    a is the IP address to listen on
    p is the port to run server on (Default: 9000)
    t is the game time in seconds (Default: 120)
"""

from getopt import getopt
import sys

from manager import ExpNimManager

if __name__ == '__main__':
    try:
        opts, args = getopt(sys.argv[1:], 'a:m:p:t:')
    except GetoptError:
        sys.stderr.write('Error parsing options\n')
        sys.stderr.write(__doc__)
        exit(-1)
    init_max = 3
    time = 120
    port = 9000
    address = ''
    for o, a in opts:
        if o == '-a':
            address = a
        elif o == '-m':
            init_max = int(a)
        elif o == '-p':
            port = int(a)
        elif o == '-t':
            time = int(t)
    try:
        init_stones = int(args[0])
        num_resets = int(args[1])
    except (IndexError, ValueError):
        sys.stderr.write(__doc__)
        exit(-1)
    game_manager = ExpNimManager(init_stones, num_resets, init_max=init_max,
                                 game_time=time, address=address, port=port)
    game_manager.run_game()
