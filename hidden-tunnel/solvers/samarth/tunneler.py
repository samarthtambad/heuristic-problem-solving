import sys
import getopt
import math
import random
from collections import defaultdict


class DisjointSet:
    def __init__(self, num_grid):
        self.parent = {}
        self.rank = {}
        for r in range(1, num_grid + 1):
            for c in range(1, num_grid + 1):
                self.parent[(r, c)] = (r, c)
                self.rank[(r, c)] = 1

    # make a and b part of the same component
    # union by rank optimization
    def union(self, a, b):
        pa = self.find(a)
        pb = self.find(b)
        if pa == pb: return
        if self.rank[pa] > self.rank[pb]:
            self.parent[pb] = pa
            self.rank[pa] += self.rank[pb]
        else:
            self.parent[pa] = pb
            self.rank[pb] += self.rank[pa]

    # find the representative of the
    # path compression optimization
    def find(self, a):
        if self.parent[a] == a:
            return a

        self.parent[a] = self.find(self.parent[a])
        return self.parent[a]


def build_tunnel(num_grid, tunnel_length, f):

    def dfs(vertex, path):
        nonlocal tunnel_verts, mst

        if vertex[0] == num_grid:
            tunnel_verts = path
            return True

        for adj_vertex in mst[vertex]:
            if adj_vertex not in path:
                path.append(adj_vertex)
                if dfs(adj_vertex, path):
                    return True

    # create graph
    graph = defaultdict(list)
    for r in range(1, num_grid + 1):
        for c in range(1, num_grid + 1):
            vertex = (r, c)
            for i, j in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_r, new_c = r + i, c + j
                if 1 <= new_r <= num_grid and 1 <= new_c <= num_grid:
                    graph[vertex].append((new_r, new_c))

    # generate random MST
    mst = defaultdict(list)
    ds = DisjointSet(num_grid)
    for u in graph.keys():
        adj_list = graph[u]
        random.shuffle(adj_list)
        for v in adj_list:
            if ds.find(u) != ds.find(v):
                ds.union(u, v)
                mst[u].append(v)
                mst[v].append(u)

    # find path by DFS on MST
    tunnel_verts = []
    tries = 0
    while True:
        tries += 1
        start = (1, random.randint(1, num_grid))
        dfs(start, [start])
        if num_grid - 1 <= len(tunnel_verts) <= tunnel_length:
            break

    print("Tries: {0}, Length of tunnel: {1}, Path: {2}".format(tries, len(tunnel_verts), tunnel_verts))
    for i in range(len(tunnel_verts) - 1):
        u, v = tunnel_verts[i], tunnel_verts[i + 1]
        f.write("{},{} {},{}\n".format(u[0], u[1], v[0], v[1]))


def build_tunnel_dfs(num_grid, tunnel_length, f):

    def dfs(vertex, path):
        nonlocal tunnel_verts, graph

        if vertex[0] == num_grid:
            tunnel_verts = path
            return True

        adj = graph[vertex]
        random.shuffle(adj)
        for adj_vertex in adj:
            if adj_vertex not in path:
                path.append(adj_vertex)
                if dfs(adj_vertex, path):
                    return True

    # create graph
    graph = defaultdict(list)
    start = (1, random.randint(1, num_grid))
    for r in range(1, num_grid + 1):
        for c in range(1, num_grid + 1):
            vertex = (r, c)
            for i, j in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_r, new_c = r + i, c + j
                if 1 <= new_r <= num_grid and 1 <= new_c <= num_grid:
                    graph[vertex].append((new_r, new_c))

    # try to create tunnel of random length
    print("Start: {0}".format(start))
    tunnel_verts = []
    tries = 0
    while True:
        tries += 1
        dfs(start, [start])
        if num_grid - 1 <= len(tunnel_verts) <= tunnel_length:
            break

    print("Tries: {0}, Length of tunnel: {1}, Path: {2}".format(tries, len(tunnel_verts), tunnel_verts))
    for i in range(len(tunnel_verts)-1):
        u, v = tunnel_verts[i], tunnel_verts[i+1]
        f.write("{},{} {},{}\n".format(u[0], u[1], v[0], v[1]))


def build_tunnel_backtracking(num_grid, tunnel_length, f):

    def dfs(depth, vertex, target, path):
        nonlocal tunnel_verts
        if vertex == target and depth == 0:
            tunnel_verts = path
            return True
        if depth == 0:
            return False
        for adj_vertex in graph[vertex]:
            if adj_vertex not in path:
                path.append(adj_vertex)
                if dfs(depth-1, adj_vertex, target, path):
                    return True
                path.pop()

    # create graph
    graph = defaultdict(list)
    start, target = (1, random.randint(1, num_grid)), (num_grid, random.randint(1, num_grid))
    for r in range(1, num_grid + 1):
        for c in range(1, num_grid + 1):
            vertex = (r, c)
            for i, j in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_r, new_c = r + i, c + j
                if 1 <= new_r <= num_grid and 1 <= new_c <= num_grid:
                    graph[vertex].append((new_r, new_c))

    # try to create tunnel of random length
    min_tunnel_length, max_tunnel_length = num_grid - 1, min(tunnel_length, 3 * num_grid)
    print("Start: {0}, Target: {1}".format(start, target))
    tunnel_verts = []
    while True:
        tunnel_length = random.randint(min_tunnel_length, max_tunnel_length)
        print(tunnel_length)
        dfs(tunnel_length, start, target, [start])
        if len(tunnel_verts) > 0:
            break

    print(tunnel_verts)
    for i in range(len(tunnel_verts)-1):
        u, v = tunnel_verts[i], tunnel_verts[i+1]
        f.write("{},{} {},{}\n".format(u[0], u[1], v[0], v[1]))


if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], 'n:p:k:', [
        'grid=', 'phase=', 'tunnel='])
    num_grid, num_phase, tunnel_length = 0, 0, 0
    for o, a in optlist:
        if o in ("-n", "--grid"):
            num_grid = int(a)
        elif o in ("-p", "--phase"):
            num_phase = int(a)
        elif o in ("-k", "--tunnel"):
            tunnel_length = int(a)
        else:
            assert False, "unhandled option"

    f = open("tunnel", "w")
    build_tunnel(num_grid, tunnel_length, f)
    f.close()
