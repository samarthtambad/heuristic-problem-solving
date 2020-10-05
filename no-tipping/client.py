"""
client to interact with the server and play the game
"""

# Echo client program
import socket
import sys
import random
import copy
from timeit import default_timer as timer


class NoTippingClient:
    def __init__(self, host, port, first, name):
        self.host = host
        self.port = port
        self.first = first
        self.name = name
        self.stage = 0
        self.srv = None
        self.is_over = False
        self.board = [0 for i in range(61)]
        self.board[-4 + 30] = 3
        self.weights = None
        self.opponent_weights = None
        self.num_weights = None
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.connect((host, port))

        # send initial info
        self.srv.sendall('{} {}'.format(name, first).encode('utf-8'))

        # receive number of weights
        num_weights = int(self.srv.recv(1024).decode('utf-8'))
        print("Number of Weights is: " + str(num_weights))
        self.num_weights = num_weights
        self.weights = [i for i in reversed(range(1, num_weights+1))]
        self.opponent_weights = [i for i in reversed(range(1, num_weights+1))]

    def over(self):
        return self.is_over
    
    def end(self):
        self.srv.close()
    
    def update(self):
        data = self.srv.recv(1024).decode('utf-8')

        if not data:
            return False
        
        # data received, update state
        data = [int(data.split(' ')[i]) for i in range(0, 63)]
        new_board = data[1:-1]
        print("")
        print("{0} stage".format("Add" if data[0] == 0 else "Remove"))
        print(data)
        if data[0] == 0:
            for i in range(61):
                if new_board[i] != self.board[i]:
                    self.opponent_weights.remove(new_board[i])
                    break

        self.stage = data[0]
        self.board = data[1:-1]
        self.is_over = False if data[-1] == 0 else True
        return True

    def move(self):
        if not self.over():
            if self.stage == 0:  # add stage
                self.add()
            else:               # remove stage
                self.remove()
    
    def add(self):
        weight, pos = self.add_greedy()
        if weight in self.weights:
            self.weights.remove(weight)
        self.board[pos + 30] = weight
        print("Added {0} kg at position {1}".format(weight, pos))
        self.print_balance()
        self.srv.sendall("{0} {1}".format(weight, pos).encode('utf-8'))

    def remove(self):
        pos = self.minimax_strategy_remove()
        self.board[pos + 30] = 0
        print("Removed weight at position {0}".format(pos))
        self.print_balance()
        self.srv.sendall("{0}".format(pos).encode('utf-8'))

    def add_greedy(self):
        my_weights = copy.deepcopy(self.weights)
        board = copy.deepcopy(self.board)
        options = self.get_add_options(my_weights, board)
        options.sort(key=lambda x: (x[0], abs(x[1])))

        if len(options) > 0:
            return options[-1]
        
        print("No valid weight and position found to add")
        return 1, -1

    def minimax_strategy_remove(self):

        def minimax(board, maximizingPlayer, depth):

            tup = tuple(board + [1 if maximizingPlayer else 0])
            if tup in memo:
                return memo[tup]

            if maximizingPlayer:
                
                remove_options = self.get_remove_options(board)

                # nothing to remove
                if len(remove_options) == 0:
                    memo[tup] = (-1000000, None)
                    return -1000000, None

                # choose best move
                max_score, res = float('-inf'), None
                for pos in remove_options:
                    w = board[pos + 30]
                    board[pos + 30] = 0
                    score, _ = minimax(board, False, depth+1)
                    if score > max_score:
                        max_score = score
                        res = pos
                    board[pos + 30] = w
                
                memo[tup] = (max_score, res)
                return max_score, res

            else:

                remove_options = self.get_remove_options(board)

                # nothing to remove
                if len(remove_options) == 0:
                    memo[tup] = (-depth, None)
                    return -depth, None

                # choose best move
                min_score, res = float('inf'), None
                for pos in remove_options:
                    w = board[pos + 30]
                    board[pos + 30] = 0
                    score, _ = minimax(board, True, depth+1)
                    if score < min_score:
                        min_score = score
                        res = pos
                    board[pos + 30] = w

                memo[tup] = (min_score, res)
                return min_score, res

        timer_start = timer()
        memo = {}
        board = copy.deepcopy(self.board)
        remove_options = self.get_remove_options(board)
        print("options", remove_options)
        self.print_option_balance()

        # if len(remove_options) > 8:
        #     return self.remove_random()

        score, res = minimax(board, True, 0)
        print(score, res)

        timer_end = timer()
        print("Time: {0} s".format(timer_end - timer_start), file=sys.stderr)

        if res: return res

        if len(remove_options) > 0:
            return random.choice(remove_options)
        else:
            return -1

    def dfs_count_strategy_remove(self):

        def dfs(board, player):

            tup = tuple(board + [1 if player else 0])
            if tup in memo:
                return memo[tup]

            options = self.get_remove_options(board)
            print("options", options)

            if player and len(options) == 0:
                memo[tup] = 0
                return 0
            if not player and len(options) == 0:
                memo[tup] = 1
                return 1

            if player:
                count = 0
                for pos in options:
                    w = board[pos + 30]
                    board[pos + 30] = 0
                    count += dfs(board, False)
                    board[pos + 30] = w
                memo[tup] = count
                return count
            else:
                count = 0
                for pos in options:
                    w = board[pos + 30]
                    board[pos + 30] = 0
                    count += dfs(board, True)
                    board[pos + 30] = w
                memo[tup] = count
                return count

        timer_start = timer()
        memo = {}
        board = copy.deepcopy(self.board)
        options = self.get_remove_options(board)
        print("options", options)
        self.print_option_balance()

        max_count, res = float("-inf"), -1
        for pos in options:
            w = board[pos + 30]
            board[pos + 30] = 0
            count = dfs(board, False)
            print(pos, count)
            if count > max_count:
                max_count = count
                res = pos
            board[pos + 30] = w

        timer_end = timer()
        print("Time: {0} s".format(timer_end - timer_start), file=sys.stderr)

        return res

    def remove_random(self, game_board):
        board = copy.deepcopy(game_board)
        options = self.get_remove_options(board)
        if len(options) == 0:
            print("No valid remove position found")
            return -1

        return random.choice(options)

    def check_balance(self, board):
        left_torque = 0
        right_torque = 0
        for i in range(0,61):
            left_torque += (i - 30 + 3) * board[i]
            right_torque += (i - 30 + 1) * board[i]
        left_torque += 3 * 3
        right_torque += 1 * 3
        return left_torque >= 0 and right_torque <= 0

    def print_option_balance(self):
        board = copy.deepcopy(self.board)
        for pos in range(0, 61):
            if board[pos] != 0:
                weight = board[pos]
                board[pos] = 0
                left_torque = 0
                right_torque = 0
                for i in range(0, 61):
                    left_torque += (i - 30 + 3) * board[i]
                    right_torque += (i - 30 + 1) * board[i]
                left_torque += 3 * 3
                right_torque += 1 * 3
                print("Pos: {0}, Weight: {1}, Left: {2}, Right: {3}".format(pos, weight, left_torque, right_torque))

    def print_balance(self):
        board = copy.deepcopy(self.board)
        left_torque = 0
        right_torque = 0
        for i in range(0,61):
            left_torque += (i - 30 + 3) * board[i]
            right_torque += (i - 30 + 1) * board[i]
        left_torque += 3 * 3
        right_torque += 1 * 3
        print("Left: {0}, Right: {1}".format(left_torque, right_torque))

    def get_valid_positions(self, weight, game_board):
        board = copy.deepcopy(game_board)
        options = []
        for i in range(0, 61):
            if board[i] == 0:
                board[i] = weight
                if self.check_balance(board):
                    options.append(i - 30)
                board[i] = 0
        return options
    
    def get_add_options(self, weights, board):
        options = []
        for w in weights:
            for pos in self.get_valid_positions(w, board):
                options.append((w, pos))
        return options
    
    def get_remove_options(self, game_board):
        board = copy.deepcopy(game_board)
        options = []
        for i in range(0, 61):
            if board[i] != 0:
                weight = board[i]
                board[i] = 0
                if self.check_balance(board):
                    options.append(i - 30)
                board[i] = weight
        return options


if __name__ == "__main__":

    first = 0
    name = "RandomPlayer"

    # connect to server
    HOST = sys.argv[1].split(":")[0]
    PORT = int(sys.argv[1].split(":")[1]) # The same port as used by the server
    
    for idx, val in enumerate(sys.argv):
        if val == "-f":
            first = 1
        if val == "-n":
            name = sys.argv[idx + 1]

    game = NoTippingClient(HOST, PORT, first, name)

    while not game.over():

        while not game.update():
            continue

        game.move()
    
    print("Game Over")
    game.end()
