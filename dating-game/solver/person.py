import socket
import sys
import numpy as np
from dating.utils import floats_to_msg2, candidate_to_msg


class Person:
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

        initial_weights = self.get_valid_weights(self.num_attr)
        ideal_candidate = initial_weights > 0
        anti_ideal_candidate = initial_weights <= 0
        self.srv_conn.sendall(floats_to_msg2(initial_weights))
        self.srv_conn.sendall(candidate_to_msg(ideal_candidate))
        self.srv_conn.sendall(candidate_to_msg(anti_ideal_candidate))

        for i in range(20):
            # 7 char weights + commas + exclamation
            data = self.srv_conn.recv(8*self.num_attr).decode("utf-8")
            print('%d: Received guess = %r' % (i, data))
            assert data[-1] == '\n'
            self.srv_conn.send(floats_to_msg2(self.get_modified_weights(initial_weights)))

        self.srv_conn.close()

    def get_modified_weights(self, initial_weights):
        return initial_weights

    def get_valid_prob(self, n):
        alpha = np.random.random(n)
        p = np.random.dirichlet(alpha)
        p = np.trunc(p*100)/100.0

        # ensure p sums to 1 after rounding
        p[-1] = 1 - np.sum(p[:-1])
        return p

    def get_valid_weights(self, n):
        half = n//2

        a = np.zeros(n)
        a[:half] = self.get_valid_prob(half)
        a[half:] = -self.get_valid_prob(n - half)
        return np.around(a, 2)

if __name__ == '__main__':
    PORT = int(sys.argv[1])
    person = Person(PORT)
    person.run()
