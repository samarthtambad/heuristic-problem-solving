from disjoint_set import DisjointSet
from collections import defaultdict

def generate_mst(self, verts):
    num_sites = len(verts)

    # Create connected graph
    edges = []
    for i in range(num_sites):
        for j in range(i+1, num_sites):
            src, dest = verts[i], verts[j]
            dist = abs(self.x_loc[dest] - self.x_loc[src]) + abs(self.y_loc[dest] - self.y_loc[src])
            edges.append((src, dest, dist))
    
    # Find MST
    edges.sort(key=lambda x: x[2])
    ds = DisjointSet(301)
    mst = defaultdict(list)
    for src, dest, dist in edges:
        if ds.find(src) != ds.find(dest):
            ds.union(src, dest)
            mst[src].append(dest)
            mst[dest].append(src)
    
    return mst

def get_mst_path(self, mst, start):
    def dfs(u):
        path.append(u)
        visited.add(u)
        for v in mst[u]:
            if v not in visited:
                dfs(v)
    
    visited = set()
    path = []
    dfs(start)
    return path