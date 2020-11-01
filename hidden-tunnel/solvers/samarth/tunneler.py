import sys
import getopt
import math
import random
from collections import defaultdict


def build_tunnel(num_grid, f):
    min_tunnel_length, max_tunnel_length = num_grid - 1, 3 * num_grid
    tunnel_length = random.randint(min_tunnel_length, max_tunnel_length)

    def dfs(vertex, target, path):
        if len(path) > tunnel_length:
            return []
        if vertex == target and len(path) == tunnel_length:
            return path
        for adj_vertex in graph[vertex]:
            if adj_vertex not in path:
                path.add(adj_vertex)
                res = dfs(adj_vertex, target, path)
                if res:
                    return res
                path.remove(adj_vertex)

    # create graph
    graph = defaultdict(list)
    visited = set()
    start, target = (1, random.randint(1, num_grid)), (1, random.randint(1, num_grid))
    for r in range(1, num_grid + 1):
        for c in range(1, num_grid + 1):
            vertex = (r, c)
            for i, j in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_r, new_c = r + i, c + j
                if 1 <= new_r <= num_grid and 1 <= new_c <= num_grid:
                    graph[vertex].append((new_r, new_c))

    path = dfs(start, target, set(start))
    print(path)
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        f.write("{},{} {},{}\n".format(u[0], u[1], v[0], v[1]))
        print("{},{} {},{}\n".format(u[0], u[1], v[0], v[1]))


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
    build_tunnel(num_grid, f)
    f.close()
