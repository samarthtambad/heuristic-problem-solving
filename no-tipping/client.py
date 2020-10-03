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
        self.weights = None
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
        weight, pos = self.add_random()
        self.weights.remove(weight)
        print("Added {0} kg at position {1}".format(weight, pos))
        self.srv.sendall("{0} {1}".format(weight, pos).encode('utf-8'))

    def remove(self):
        pos = self.remove_random()
        print("Removed weight at position {0}".format(pos))
        self.srv.sendall("{0}".format(pos).encode('utf-8'))

    def add_random(self):
        for w in self.weights:
            positions = []
            for pos in self.get_valid_positions(w):
                positions.append(pos)
            if len(positions) == 0: continue
            print(positions)
            pos = random.choice(positions)
            return w, pos
        
        print("No valid position found")
        return 1, -1
    
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

    def get_valid_positions(self, weight):
        board = copy.deepcopy(self.board)
        for i in range(0,61):
            if board[i] == 0:
                board[i] = weight
                if self.check_balance(board):
                    board[i] = 0
                    yield (i - 30)
                board[i] = 0


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
