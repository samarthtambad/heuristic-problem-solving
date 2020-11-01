import getopt
import json
import math
import random
import socket
import sys


class Detector:
    def __init__(self, num_grid, num_phase, tunnel_length, port):
        self.player_name = 'remember_the_name'
        self.num_grid = num_grid
        self.num_phase = num_phase
        self.tunnel_length = tunnel_length
        self.port = port
        self.srv_conn = None

    def send_data(self, data):
        self.srv_conn.sendall(json.dumps(data).encode())

    def receive_data(self):
        DATA_SIZE = 4096
        while True:
            data = self.srv_conn.recv(DATA_SIZE).decode()
            if data:
                return json.loads(data)

    def run_detector(self):
        # establish connection
        self.srv_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_conn.connect(('localhost', self.port))

        # send team name
        data = {'player_name': self.player_name}
        self.send_data(data)

        # receive initial data
        res = self.receive_data()
        self.num_grid = res['grid']
        self.num_phase = res['remaining_phases']
        self.tunnel_length = res['tunnel_length']

        # probe phases
        for i in range(self.num_phase - 1):
            payload = {'phase': 'probe', 'probes': []}
            probes = self.get_probes()
            payload['probes'] = probes
            print("Probe {}, payload: {}".format(i+1, payload))
            self.send_data(payload)
            res = self.receive_data()
            print(res)  # gets probing report

        # guess phase
        guess = self.make_guess()
        payload = {'phase': 'guess', 'answer': guess}
        print("Guess, payload: {}".format(payload))
        self.send_data(payload)
        self.srv_conn.close()

    def get_probes(self):
        for i in range(3):
            probes = []
            x = math.ceil(random.random() * (num_grid))
            y = math.floor(random.random() * (num_grid))
            if [x, y] not in probes:
                # for the ease of decoding, please avoid using python tuples
                probes.append([x, y])
        return probes

    def make_guess(self):
        return [[1, 3], [2, 3]], [[2, 3], [3, 3]], [[3, 3], [4, 3]], [[4, 3], [5, 3]]


if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], 'n:p:k:', [
        'grid=', 'phase=', 'tunnel=', 'port='])
    num_grid, num_phase, tunnel_length, port = 0, 0, 0, 8000
    for o, a in optlist:
        if o in ('-n', '--grid'):
            num_grid = int(a)
        elif o in ('-p', '--phase'):
            num_phase = int(a)
        elif o in ('-k', '--tunnel'):
            tunnel_length = int(a)
        elif o in ('--port'):
            port = int(a)
        else:
            assert False, 'unhandled option'

    d = Detector(num_grid, num_phase, tunnel_length, port)
    d.run_detector()
