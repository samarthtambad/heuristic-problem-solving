import sys
import getopt
import math
import random
from collections import defaultdict


def build_tunnel(num_grid, tunnel_length, f):

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
