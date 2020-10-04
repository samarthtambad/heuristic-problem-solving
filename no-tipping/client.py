"""
client to interact with the server and play the game
"""

# Echo client program
import socket
import sys
import random
import copy

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

        # send initial info to server
        for idx, val in enumerate(sys.argv):
            if(val == "-f"): 
                first = 1
            if(val == "-n"):
                name = sys.argv[idx + 1]

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
        print(data)
        new_board = data[1:-1]
        if data[0] == 0:
            for i in range(61):
                if new_board[i] != self.board[i]:
                    self.opponent_weights.remove(new_board[i])
                    break
        print("opponent_weights", self.opponent_weights)
        self.stage = data[0]
        self.board = data[1:-1]
        self.is_over = False if data[-1] == 0 else True

        return True

    def move(self):
        if self.stage == 0: # add stage
            self.add()
        else:               # remove stage
            self.remove()
    
    def add(self):
        weight, pos = self.minimax_strategy() # self.add_random()
        self.weights.remove(weight)
        self.board[pos + 30] = weight
        print("Added {0} kg at position {1}".format(weight, pos))
        self.srv.sendall("{0} {1}".format(weight, pos).encode('utf-8'))

    def remove(self):
        pos = self.remove_random()
        self.board[pos + 30] = 0
        print("Removed weight at position {0}".format(pos))
        self.srv.sendall("{0}".format(pos).encode('utf-8'))

    def add_random(self):
        board = copy.deepcopy(self.board)
        for w in self.weights:
            positions = []
            for pos in self.get_valid_positions(w, board):
                positions.append(pos)
            if len(positions) == 0: continue
            print(positions)
            pos = random.choice(positions)
            return w, pos
        
        print("No valid position found")
        return 1, -1

    # def add_backtracking(self):

    #     def backtrack(my_weights, opponent_weights, board, player):
    #         print("backtrack", my_weights, opponent_weights, board, player)

    #         tup = tuple(tuple(my_weights) + tuple(opponent_weights) + tuple(board) + tuple([1 if player else 0]))
    #         if tup in memo:
    #             return memo[tup]

    #         if player:
    #             if len(my_weights) > 0: # add stage
    #                 options = []
    #                 for w in my_weights:
    #                     for pos in self.get_valid_positions(w, board):
    #                         options.append((w, pos))

    #                 # base case
    #                 if len(options) == 0: return 0
                    
    #                 count = 0
    #                 for w, pos in options:
    #                     idx = my_weights.index(w)
    #                     my_weights.pop(idx)
    #                     board[pos + 30] = w
    #                     count += backtrack(my_weights, opponent_weights, board, not player)
    #                     my_weights.insert(idx, w)
    #                     board[pos + 30] = 0
                    
    #                 memo[tup] = count
    #                 return count

    #             else:   # remove stage
    #                 options = []
    #                 for pos in self.get_valid_remove_positions(board):
    #                     options.append(pos)
                    
    #                 # base case
    #                 if len(options) == 0: return 0

    #                 count = 0
    #                 for pos in options:
    #                     w = board[pos + 30]
    #                     board[pos + 30] = 0
    #                     count += backtrack(my_weights, opponent_weights, board, not player)
    #                     board[pos + 30] = w
                    
    #                 memo[tup] = count
    #                 return count
    #         else:
    #             if len(opponent_weights) > 0: # add stage
    #                 options = []
    #                 for w in opponent_weights:
    #                     for pos in self.get_valid_positions(w, board):
    #                         options.append((w, pos))

    #                 # base case
    #                 if len(options) == 0: return 1
                    
    #                 count = 0
    #                 for w, pos in options:
    #                     idx = opponent_weights.index(w)
    #                     opponent_weights.pop(idx)
    #                     board[pos + 30] = w
    #                     count += backtrack(opponent_weights, opponent_weights, board, not player)
    #                     opponent_weights.insert(idx, w)
    #                     board[pos + 30] = 0
                    
    #                 memo[tup] = count
    #                 return count

    #             else:   # remove stage
    #                 options = []
    #                 for pos in self.get_valid_remove_positions(board):
    #                     options.append(pos)
                    
    #                 # base case
    #                 if len(options) == 0: return 1

    #                 count = 0
    #                 for pos in options:
    #                     w = board[pos + 30]
    #                     board[pos + 30] = 0
    #                     count += backtrack(my_weights, opponent_weights, board, not player)
    #                     board[pos + 30] = w
                    
    #                 memo[tup] = count
    #                 return count

    #     my_weights = copy.deepcopy(self.weights)
    #     opponent_weights = copy.deepcopy(self.opponent_weights)
    #     board = copy.deepcopy(self.board)

    #     options = []
    #     for w in my_weights:
    #         for pos in self.get_valid_positions(w, board):
    #             options.append((w, pos))

    #     print(options)

    #     memo = {}

    #     max_count, res = 0, None
    #     for w, pos in options:
    #         idx = my_weights.index(w)
    #         my_weights.pop(idx)
    #         board[pos + 30] = w
    #         count = backtrack(my_weights, opponent_weights, board, False)
    #         break
    #         # print(w, pos, count)
    #         if count > max_count:
    #             max_count = count
    #             res = (w, pos)
    #         my_weights.insert(idx, w)
    #         board[pos + 30] = 0
        
    #     return res

    def minimax_strategy(self):

        def minimax(my_weights, opponent_weights, board, maximizingPlayer):

            if maximizingPlayer:
                
                if len(my_weights) > 0: # add stage
                    add_options = self.get_add_options(board)

                    # nothing to add
                    if len(add_options) == 0:
                        return -1, None

                    # choose best move
                    max_score, res = float('-inf'), None
                    for w, pos in add_options:
                        idx = my_weights.index(w)
                        my_weights.pop(idx)
                        board[pos + 30] = w
                        score, ans = minimax(my_weights, opponent_weights, board, False)
                        if score > max_score:
                            max_score = score
                            res = (w, pos)
                        my_weights.insert(idx, w)
                        board[pos + 30] = 0
                    return max_score, res
                
                else:   # remove stage
                    remove_options = self.get_remove_options(board)

                    # nothing to remove
                    if len(remove_options) == 0:
                        return -1, None

                    # choose best move
                    max_score, res = float('-inf'), None
                    for pos in remove_options:
                        w = board[pos + 30]
                        board[pos + 30] = 0
                        score, ans = minimax(my_weights, opponent_weights, board, False)
                        if score > max_score:
                            max_score = score
                            res = (None, pos)
                        board[pos + 30] = w
                    return max_score, res

            else:
                if len(opponent_weights) > 0: # add stage
                    add_options = self.get_add_options(board)

                    # nothing to add
                    if len(add_options) == 0:
                        return -1, None

                    # choose best move
                    min_score, res = float('inf'), None
                    for w, pos in add_options:
                        idx = opponent_weights.index(w)
                        opponent_weights.pop(idx)
                        board[pos + 30] = w
                        score, ans = minimax(my_weights, opponent_weights, board, True)
                        if score < min_score:
                            min_score = score
                            res = (w, pos)
                        opponent_weights.insert(idx, w)
                        board[pos + 30] = 0
                    return min_score, res
                
                else:   # remove stage
                    remove_options = self.get_remove_options(board)

                    # nothing to remove
                    if len(remove_options) == 0:
                        return -1, None

                    # choose best move
                    min_score, res = float('inf'), None
                    for pos in remove_options:
                        w = board[pos + 30]
                        board[pos + 30] = 0
                        score, ans = minimax(my_weights, opponent_weights, board, True)
                        if score < min_score:
                            min_score = score
                            res = (None, pos)
                        board[pos + 30] = w
                    return min_score, res

        my_weights = copy.deepcopy(self.weights)
        opponent_weights = copy.deepcopy(self.opponent_weights)
        board = copy.deepcopy(self.board)

        return minimax(my_weights, opponent_weights, board, True)

    
    def remove_random(self):
        board = copy.deepcopy(self.board)
        for i, w in enumerate(board):
            if w != 0:
                board[i] = 0
                if self.check_balance(board):
                    return (i - 30)
                board[i] = w
        
        print("No valid position found")
        return -1

    def check_balance(self, board):
        left_torque = 0
        right_torque = 0
        for i in range(0,61):
            left_torque += (i - 30 + 3) * board[i]
            right_torque += (i - 30 + 1) * board[i]
        left_torque += 3 * 3
        right_torque += 1 * 3
        return left_torque >= 0 and right_torque <= 0

    def get_valid_positions(self, weight, board):
        for i in range(0,61):
            if board[i] == 0:
                board[i] = weight
                if self.check_balance(board):
                    board[i] = 0
                    yield (i - 30)
                board[i] = 0
    
    def get_add_options(self, board):
        my_weights = copy.deepcopy(self.weights)
        options = []
        for w in my_weights:
            for pos in self.get_valid_positions(w, board):
                options.append((w, pos))
        return options
    
    def get_remove_options(self, board):
        options = []
        for pos in self.get_valid_remove_positions(board):
            options.append(pos)
        return options

    def get_valid_remove_positions(self, board):
        for i in range(0,61):
            if board[i] != 0:
                weight = board[i]
                board[i] = 0
                if self.check_balance(board):
                    board[i] = weight
                    yield (i - 30)
                board[i] = weight


if __name__ == "__main__":

    first = 0
    name = "RandomPlayer"

    # connect to server
    HOST = sys.argv[1].split(":")[0]
    PORT = int(sys.argv[1].split(":")[1]) # The same port as used by the server
    
    for idx, val in enumerate(sys.argv):
        if(val == "-f"): 
            first = 1
        if(val == "-n"):
            name = sys.argv[idx + 1]

    game = NoTippingClient(HOST, PORT, first, name)

    while not game.over():

        while not game.update():
            continue

        game.move()
    
    print("Game Over")
    game.end()
