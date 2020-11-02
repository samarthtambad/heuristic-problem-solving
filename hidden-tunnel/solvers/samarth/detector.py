import getopt
import json
import math
import random
import socket
import sys
from collections import defaultdict, deque

DATA_SIZE = 8192  # 4096

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
        self.tunnel = set()
        self.start_vertices = []
        self.end_vertices = []

    def send_data(self, data):
        self.srv_conn.sendall(json.dumps(data).encode())

    def receive_data(self):
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
        # print(self.graph)

        # probe phases
        for i in range(self.num_phase - 1):
            payload = {'phase': 'probe', 'probes': []}
            probes = self.get_probes(i+1)
            payload['probes'] = probes
            print("\nProbe {}, payload: {}".format(i+1, payload))
            self.send_data(payload)
            res = self.receive_data()
            print(res)  # gets probing report
            self.update(probes, res['result'])

        # guess phase
        guess = self.make_guess()
        payload = {'phase': 'guess', 'answer': guess}
        print("\nGuess, payload: {}".format(payload))
        self.send_data(payload)
        self.srv_conn.close()

    def get_probes_all(self):
        probes = []
        for vertex in self.graph.keys():
            if vertex not in self.prev_probes and vertex not in self.eliminated:
                self.prev_probes.add(vertex)
                probes.append([vertex[0], vertex[1]])
        return probes

    def get_probes_alternate(self, probe_num):
        if probe_num == self.num_phase - 1:     # last probe phase
            self.eliminate_vertices()
            return self.get_probes_all()

        probes = []
        if probe_num == 1:  # probe end rows
            for r, c in self.graph.keys():
                if r == 1 or r == self.num_grid:
                    probes.append([r, c])
        else:
            self.eliminate_vertices()
            no_probe = set()
            for vertex in self.graph.keys():
                if vertex not in no_probe:
                    probes.append([vertex[0], vertex[1]])
                    no_probe.add(vertex)
                    for adj in self.graph[vertex]:
                        no_probe.add(adj)
        return probes

    def get_probes(self, probe_num):
        probe_rows = set()
        probe_rows.add(1)
        probe_rows.add(self.num_grid)

        for r in range(2, self.num_grid):
            if r % 2 == 1:
                probe_rows.add(r)

        probes = []
        if probe_num == 1: 
            for vertex in self.graph.keys():
                if vertex[0] in probe_rows:
                    self.prev_probes.add(vertex)
                    probes.append([vertex[0], vertex[1]])
        
        return probes

    def eliminate_vertices(self):
        q = deque()
        visited = set()
        start = self.start_vertices[0]
        q.append(start)
        visited.add(start)

        # BFS to find vertices that can be reached
        while q:
            size = len(q)
            for _ in range(size):
                u = q.popleft()
                for v in self.graph[u]:
                    if v not in self.eliminated:
                        if v not in visited:
                            visited.add(v)
                            q.append(v)

        # eliminate vertices that can't be reached
        elim = []
        for vertex in self.graph.keys():
            if vertex not in visited:
                elim.append(vertex)
                self.eliminated.add(vertex)

        print("Eliminated: {0}".format(elim))

    def update(self, probes, result):
        if len(result) == 0:
            return

        for res_dict in result:
            for key, values in res_dict.items():
                v = list(map(int, key[1:-1].split(",")))
                vertex = (v[0], v[1])
                if vertex[0] == 1:
                    self.start_vertices.append(vertex)
                if vertex[0] == self.num_grid:
                    self.end_vertices.append(vertex)
                for r, c in values:
                    self.tunnel.add(vertex)
                    self.tunnel.add((r, c))
                    if (r, c) not in self.tunnel_graph[vertex]:
                        self.tunnel_graph[vertex].append((r, c))

        elim = []
        for r, c in probes:
            if (r, c) not in self.tunnel:
                elim.append((r, c))
                self.eliminated.add((r, c))

        print("Tunnel Graph: {0}".format(self.tunnel_graph))
        print("Eliminated: {0}".format(elim))

    def make_guess(self):

        def dfs2(u):
            if u not in visited:
                visited.add(u)
                for v in self.tunnel_graph[u]:
                    if v not in visited:
                        res.append([[u[0], u[1]], [v[0], v[1]]])
                        dfs(v)
        
        def dfs(u, path):
            nonlocal result_path, target
            # print(path)
            if u == target:
                result_path = path
                print(path)
                return True

            if u not in visited:
                visited.add(u)
                if u in self.tunnel_graph:
                    for v in self.tunnel_graph[u]:
                        if v not in visited:
                            path.append(v)
                            if dfs(v, path): return True
                            path.pop()

                elif u not in self.eliminated:
                    for v in self.graph[u]:
                        if v not in visited and v not in self.eliminated:
                            if v not in self.tunnel_graph:
                                path.append(v)
                                if dfs(v, path): return True
                                path.pop()
                            else:
                                if u in self.tunnel_graph[v]:
                                    path.append(v)
                                    if dfs(v, path): return True
                                    path.pop()
        
        extremities = []
        for vertex, adj in self.tunnel_graph.items():
            if len(adj) == 1:
                extremities.append(vertex)

        result_path = []
        visited = set()
        start, target = extremities[0], extremities[1]
        dfs(start, [start])
        print(extremities)
        print("Start: {0}, Target: {1}".format(start, target))
        print("Guess Path: {0}".format(result_path))

        res = []
        for i in range(len(result_path) - 1):
            u, v = result_path[i], result_path[i + 1]
            res.append([[u[0], u[1]], [v[0], v[1]]])

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
