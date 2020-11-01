import getopt
import json
import math
import random
import socket
import sys
from collections import defaultdict

class Detector:
    def __init__(self, num_grid, num_phase, tunnel_length, port):
        self.player_name = 'remember_the_name'
        self.num_grid = num_grid
        self.num_phase = num_phase
        self.tunnel_length = tunnel_length
        self.port = port
        self.srv_conn = None
        self.graph = defaultdict(list)
        self.prev_probes = set()
        self.eliminated = set()
        self.tunnel_graph = defaultdict(list)

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

        # create graph
        for r in range(1, self.num_grid + 1):
            for c in range(1, self.num_grid + 1):
                vertex = (r, c)
                for i, j in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_r, new_c = r + i, c + j
                    if 1 <= new_r <= self.num_grid and 1 <= new_c <= self.num_grid:
                        self.graph[vertex].append((new_r, new_c))
        print(self.graph)

        # probe phases
        for i in range(self.num_phase - 1):
            payload = {'phase': 'probe', 'probes': []}
            probes = self.get_probes()
            payload['probes'] = probes
            print("Probe {}, payload: {}".format(i+1, payload))
            self.send_data(payload)
            res = self.receive_data()
            print(res)  # gets probing report
            self.update(probes, res['result'][0])

        # guess phase
        guess = self.make_guess()
        payload = {'phase': 'guess', 'answer': guess}
        print("Guess, payload: {}".format(payload))
        self.send_data(payload)
        self.srv_conn.close()

    def get_probes(self):
        probes = []
        for vertex in self.graph.keys():
            if vertex not in self.prev_probes:
                self.prev_probes.add(vertex)
                probes.append([vertex[0], vertex[1]])
        # for i in range(3):
        #     probes = []
        #     x = math.ceil(random.random() * self.num_grid)
        #     y = math.floor(random.random() * self.num_grid)
        #     if [x, y] not in probes:
        #         # for the ease of decoding, please avoid using python tuples
        #         probes.append([x, y])
        return probes

    def update(self, probes, response):
        print(response)
        for r, c in probes:
            vertex = (r, c)
            vertex_str = "[{0},{1}]".format(r, c)
            self.eliminated.add(vertex)
            if vertex_str in response:
                for adj in response[vertex_str]:
                    self.tunnel_graph[vertex].append(adj)

    def make_guess(self):
        res = []
        visited = set()
        for vertex, adj in self.tunnel_graph.items():
            for next in adj:
                if next not in visited:
                    visited.add(next)
                    res.append([[vertex[0], vertex[1]], [next[0], next[1]]])

        return res


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
