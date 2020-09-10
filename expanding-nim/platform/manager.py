# -*- coding: utf-8 -*-
"""
This file contains the game manger for the Expanding Nim problem.
It defines the rules of the game including whose turn it is, whether
the game has ended or not, number of resets left and winner.

@author: Munir Contractor <mmc691@nyu.edu>
"""

from datetime import datetime
import json

from server import Server


class Player():
    """The class that represents the Expanding Nim player

    This is just a dictionary proxy to make sure only required
    keys are available and created.
    """

    def __init__(self, name, num_resets):
        """
        Args:
            **name:** Name of the player.\n
            **init_stones:** The number of stones player has at start of the
            game.\n
            **num_resets:** The number of resets available to the player at
            the start of the game.
        """
        self._dict = {'resets_left': num_resets,
                      'time_taken': 0,
                      'name': name,
                      }
        self.prev_time = None

    def __setitem__(self, key, item):
        if key not in self._dict:
            raise KeyError('Key %s is not defined.' % key)
        self._dict[key] = item

    def __getitem__(self, key):
        return self._dict[key]


class ExpNimManager():
    """The class that represents the Expanding Nim game manager"""

    def __init__(self, init_stones, num_resets, init_max=3, game_time=120,
                 address='', port=9000):
        """
        Args:
            **init_stones:** Number of stones at the start.\n
            **num_resets:** Number of resets available to each team.\n
            **init_max:** Maximum number of stones that can be removed in
            the first move. Default is 3.\n
            **player_names:** Names of the players. This must be a list or
            tuple of 2 elements\n
            **game_time:** The time in seconds after which game will be
            timed out.
        """
        self.players = [Player('0', num_resets),
                        Player('1', num_resets)]
        self.stones_left = init_stones
        self.init_resets = num_resets
        self.current_max = init_max
        self.__init_max = init_max
        self.__game_state = {'finished': False,
                             'winner': None,
                             'reason': None,
                             'player_0': self.players[0],
                             'player_1': self.players[1],
                             }
        # Start with player 0
        self.__previous_player = 1
        self.__over = False
        self.__time_limit = game_time
        self.__prev_time = None
        self.__server = Server(address, port)
        self.__max_before_reset = None
        self.__log = open('game-log.txt', 'w+')

    def __del__(self):
        self.close()

    def close(self):
        self.__log.close()
        self.__server.close()

    def __reset(self, player_number):
        """Resets the maximum number of stones that can be removed

        The maximum number of stones that can be removed in the next turn will
        be the same as in the first move (``init_max`` in ``__init__`` call).

        Args:
            **player_number:** The player who used the reset. This is either
            0 or 1.

        Return:
            ``True`` if the reset was successful, ``False`` if the player had
            no more resets left.

        Raises:
            **ValueError:** If the ``player_number`` is not 0 or 1.
        """
        player = self.players[player_number]
        if player['resets_left'] > 0:
            player['resets_left'] -= 1
            self.__max_before_reset = self.current_max
            self.current_max = self.__init_max
            return True
        else:
            return False

    def __take_stones(self, player_number, num_stones):
        """Takes ``num_stones`` stones from ``player``

        This method represents the moves made by the player. It checks whether
        the move is valid or not and returns the status accordingly.

        Args:
            **player_number:** The player who is making the move. This is
            either 0 or 1.\n
            **num_stones:** The number of stones the player intends to take.
            If this is greater than the number of stones remaining, all stones
            will be removed and the game will end.

        Return:
            ``True`` if the move was valid; ``False`` otherwise.

        Raises:
            **ValueError:** If the ``player_number`` is not 0 or 1.
        """
        if not (0 < num_stones <= self.current_max):
            return False
        player = self.players[player_number]
        self.stones_left -= min(num_stones, self.stones_left)
        if self.__max_before_reset:
            self.current_max = self.__max_before_reset
            self.__max_before_reset = None
        self.current_max = max(num_stones + 1, self.current_max)
        return True

    def move(self, player_number, num_stones, reset=False):
        """The main method for making a move in the game

        This is the main public method of the class and the only way to
        interact with the game. It checks whether the move is valid, makes the
        move and returns the state of the game as a dict.

        Args:
            **player_number:** The number of the player making the move. This
            must be either 0 or 1.\n
            **num_stones:** The number of stones being removed in the move\n
            **reset:** Boolean value indicating whether the player wants to
            reset the maximum number of stones for the next move

        Return:
            A dict indicating the state of the game
        """
        game_state = {}
        if player_number not in (0, 1):
            raise IndexError('player_number must be 0 or 1')

        # Update the time taken and time left
        recv_time = datetime.now()
        prev_time = self.players[player_number].prev_time
        if prev_time is not None:
            time_taken = (recv_time - prev_time).total_seconds()
            self.players[player_number]['time_taken'] += time_taken

        if self.__over:
            # Game is already over
            game_state.update(self.__game_state)
        elif self.players[player_number]['time_taken'] > self.__time_limit:
            # Game time over
            game_state['finished'] = True
            game_state['winner'] = self.players[1 - player_number]['name']
            game_state['reason'] = ('Player %s exceeded time limit' %
                                    self.players[player_number]['name'])
        elif player_number == self.__previous_player:
            # Player moved out of turn
            game_state['finished'] = True
            game_state['winner'] = self.players[1 - player_number]['name']
            game_state['reason'] = ('Player %s moved out of turn' %
                                    self.players[player_number]['name'])
        elif not self.__take_stones(player_number, num_stones):
            # Move is illegal
            game_state['finished'] = True
            game_state['winner'] = self.players[1 - player_number]['name']
            game_state['reason'] = ('Player %s made an illegal move' %
                                    self.players[player_number]['name'])
        elif reset and not self.__reset(player_number):
            # Reset used illegally
            game_state['finished'] = True
            game_state['winner'] = self.players[1 - player_number]['name']
            game_state['reason'] = ('Player %s used too many resets' %
                                    self.players[player_number]['name'])
        elif self.stones_left == 0:
            # Player won the game
            game_state['finished'] = True
            game_state['winner'] = self.players[player_number]['name']
            game_state['reason'] = ('Player %s won the game! Congrats!' %
                                    self.players[player_number]['name'])
        else:
            # Normal game continues
            game_state['finished'] = False
            self.__previous_player = player_number

        game_state['current_max'] = self.current_max
        game_state['stones_left'] = self.stones_left
        game_state['stones_removed'] = num_stones
        game_state['reset_used'] = bool(reset)

        self.__game_state.update(game_state)
        self.players[1 - player_number].prev_time = datetime.now()
        self.__over = game_state['finished']
        game_state['player_0'] = self.players[0]._dict
        game_state['player_1'] = self.players[1]._dict
        self.print_status(game_state, self.players[player_number]['name'])
        return game_state

    def run_game(self):
        """Runs the game

        This method should be called once the class is instantiated
        """
        data = self.__server.establish_connections()
        players_data = list(map(lambda x: json.loads(x.decode('utf-8')), data))
        if players_data[1]['order'] == 0:
            players_data.reverse()
            self.__server.player_sockets.reverse()
        self.players[0]['name'] = players_data[0]['name']
        self.players[1]['name'] = players_data[1]['name']
        self.__server.update_all_clients(
                bytes(json.dumps({'init_stones': self.stones_left,
                                  'init_resets': self.init_resets}), 'utf-8'))
        self.players[0].prev_time = datetime.now()

        while True:
            player = 1 - self.__previous_player
            next_move = json.loads(self.__server.receive(player)
                                   .decode('utf-8'))
            game_state = self.move(player,
                                   next_move['num_stones'],
                                   next_move['reset'])
            game_state_bytes = bytes(json.dumps(game_state), 'utf-8')
            self.__server.update_all_clients(game_state_bytes)
            if game_state['finished']:
                self.close()
                exit(0)

    def print_status(self, state, player_name):
        """Prints the status of the game after each move to a log file"""
        self.__log.write('Player %s took %d stones%s\n' % (
                         player_name, state['stones_removed'],
                         ' and used reset.' if state['reset_used'] else '.'))
        self.__log.write('Current max: %d\n' % state['current_max'])
        self.__log.write('Stones left: %d\n' % state['stones_left'])
        self.__log.write('---------------------------------------\n')
        if state['finished']:
            self.__log.write('Game over\n%s\n' % state['reason'])
