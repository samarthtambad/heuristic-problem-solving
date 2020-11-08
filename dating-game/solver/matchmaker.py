import socket
import sys
import numpy as np
from dating.utils import floats_to_msg4

class MatchMaker:
    def __init__(self, port):
        self.port = port
        self.srv_conn = None
        self.num_attr = None

    def run(self):
        # establish connection
        self.srv_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_conn.connect(('localhost', self.port))

        # receive number of attributes
        num_string = self.srv_conn.recv(4).decode("utf-8")
        assert num_string.endswith('\n')
        self.num_attr = int(num_string[:-1])
        print("Number of attributes: {0}\n".format(self.num_attr))

        # fetch initial candidate scores and attributes
        print('20 Initial candidate scores and attributes:')
        for i in range(20):
            # score digits + binary labels + commas + exclamation
            data = self.srv_conn.recv(8 + 2*self.num_attr).decode("utf-8")
            print('Score = %s' % data[:8])
            assert data[-1] == '\n'
        
        # send 20 guesses
        for i in range(20):
            #Guess Weights
            guess_weights = np.random.random(self.num_attr) 
            self.srv_conn.sendall(floats_to_msg4(guess_weights))

            data = self.srv_conn.recv(8).decode('utf-8')
            assert data[-1] == '\n'
            score = float(data[:-1])
            print('Received a score = %f for i = %d ' % (score, i))
        
        self.srv_conn.close()


if __name__ == '__main__':
    PORT = int(sys.argv[1])
    matchmaker = MatchMaker(PORT)
    matchmaker.run()
