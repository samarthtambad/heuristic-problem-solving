#!/usr/bin/python3
# vim:ts=2:sts=2:sw=2

import sys
import random
from itertools import permutations
from collections import defaultdict
from timeit import default_timer as timer

timer_start = timer()

class DisjointSet:
    def __init__(self, n):
        self.parent = [i for i in range(n)]
        self.rank = [1 for _ in range(n)]
    
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


class OptimalTouring:
    def __init__(self, n_site=0, n_day=0):
      self.max_days = 10
      self.max_sites = 200
      self.num_sites = n_site
      self.num_days = n_day
      self.x = [0 for i in range(self.max_sites)]
      self.y = [0 for i in range(self.max_sites)]
      self.val = [0. for i in range(self.max_sites)]
      self.time = [0 for i in range(self.max_sites)]
      self.beghr = [[0 for i in range(self.max_days)] for j in range(self.max_sites)]
      self.endhr = [[0 for i in range(self.max_days)] for j in range(self.max_sites)]
      self.latest_start = [[0 for i in range(self.max_days)] for j in range(self.max_sites)]
      self.mst = defaultdict(list)
      self.read_input()
      for site in range(1, self.num_sites + 1):
        for day in range(1, self.num_days + 1):
          time_at_site = self.time[site]/60
          self.latest_start[site][day] = (self.endhr[site][day] - time_at_site) if (self.endhr[site][day] - time_at_site >= self.beghr[site][day]) else None

    def read_input(self):
      state = 0
      for line in sys.stdin:
        ln = line.split()
        if not ln:
          continue
        if state == 0:
          # site avenue street desiredtime value
          state = 1
        elif state == 1:
          if ln[0][0].isdigit():
            site = int(ln[0])
            self.x[site] = int(ln[1])
            self.y[site] = int(ln[2])
            self.time[site] = int(ln[3])
            self.val[site] = float(ln[4])
            self.num_sites = max(self.num_sites, site)
          else:
            # site day beginhour endhour
            state = 2
        elif state == 2:
          site = int(ln[0])
          day = int(ln[1])
          self.beghr[site][day] = int(ln[2])
          self.endhr[site][day]  = int(ln[3])
          self.num_days = max(self.num_days, day)

    def print_data(self):
      print("Num Sites: {0}, Num Days: {1}".format(self.num_sites, self.num_days))
      print("X Location: {0}".format(self.x[:self.num_sites+1]))
      print("Y Location: {0}".format(self.y[:self.num_sites+1]))
      print("Desired Time: {0}".format(self.time[:self.num_sites+1]))
      print("Value: {0}".format(self.val[:self.num_sites+1]))
      print("Begin Hour: {0}".format(self.beghr[:self.num_sites+1][:self.num_days+1]))
      print("End Hour: {0}".format(self.endhr[:self.num_sites+1][:self.num_days+1]))

    def generate_mst(self):
      edges = []
      for src in range(1, self.num_sites+1):
        for dest in range(src+1, self.num_sites+1):
          dist = abs(self.x[dest] - self.x[src]) + abs(self.y[dest] - self.y[src])
          edges.append((src, dest, dist))
      
      edges.sort(key=lambda x: x[2])

      ds = DisjointSet(self.num_sites+1)
      for src, dest, dist in edges:
        if ds.find(src) != ds.find(dest):
          ds.union(src, dest)
          self.mst[src].append(dest)
          self.mst[dest].append(src)

    def get_sites(self, day, time):
      res = []
      for site in range(1, self.num_sites + 1):
        if self.latest_start[site][day] is not None and self.beghr[site][day] <= time <= self.latest_start[site][day]:
          res.append(site)
      return res
    
    def get_next_time(self, day, time):
      res = float('inf')
      for site in range(1, self.num_sites + 1):
        start = self.beghr[site][day]
        if start > time:
          res = min(res, start)
      return res if res != float('inf') else None

    def get_valid_tour(self, visit_seq):
      res = []
      total_value = 0
      day, i = 1, 0

      while day <= self.num_days and i < len(visit_seq):
        time = 0
        prev = None
        visit = []
        while time < 24 and i < len(visit_seq):
          site = visit_seq[i]
          
          if time < self.beghr[site][day]:
            time = self.beghr[site][day]
            continue
          
          time_to_site = 0 if prev is None else (abs(self.x[site] - self.x[prev]) + abs(self.y[site] - self.y[prev]))/60
          time_at_site = self.time[site]/60

          if not self.latest_start[site][day] or time + time_to_site + time_at_site > self.latest_start[site][day]:
            i += 1
            break
          
          time = int(time + time_to_site + time_at_site)
          visit.append(site)
          total_value += self.val[site]
          i += 1
          prev = site
        
        res.append(visit)
        day += 1

      return res, total_value

    def get_mst_path(self, start):
      def dfs(u):
        path.append(u)
        visited.add(u)
        for v in self.mst[u]:
          if v not in visited:
            dfs(v)
        
      visited = set()
      path = []
      dfs(start)
      return path

    def swap_2opt(self, route, i, j):
      return route[:i] + route[i:j+1][::-1] + route[j+1:]
    
    def two_opt(self, route):
      best, max_val, res = route, 0, None
      improved = True
      while improved:
        improved = False
        for i in range(len(route)):
          if (timer() - timer_start) > 1.9: break
          for j in range(i + 1, len(route)):
            if (timer() - timer_start) > 1.9: break
            if j - i == 0: continue
            # if j - i == 1: continue
            new_route = self.swap_2opt(route, i, j)
            ans, val = self.get_valid_tour(new_route)
            if val > max_val:
              best = new_route
              max_val = val
              res = ans
              improved = True
        
        route = best
      
      return res

    def generate_mst_tour(self):
      best_path, res, max_val = None, None, 0
      for start in range(1, self.num_sites + 1):
        path = self.get_mst_path(start)
        ans, val = self.get_valid_tour(path)
        if val > max_val:
          best_path = path
          max_val = val
          res = ans

      return res
      # return self.two_opt(best_path)

    def generate_tour(self):
      sites = [site for site in range(1, self.num_sites + 1)]
      iterations = 50000
      res, max_val = None, 0
      for _ in range(iterations):
        i, j = random.randint(0, len(sites)-1), random.randint(0, len(sites)-1)
        new_seq = [s for s in sites]
        new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
        ans, val = self.get_valid_tour(new_seq)
        if val > max_val:
          max_val = val
          res = ans
        if iterations == 0: break
        iterations -= 1
      return res


# Also, you may want to modify the following function. It does nothing but
# print #day lines, each of which contains #site numbers: 1 2 3 ... #site.
def main():
  timer_start = timer()
  optimal_touring = OptimalTouring()
  # optimal_touring.print_data()
  optimal_touring.generate_mst()

  # graph = defaultdict(list)
  # graph[1] = [2]
  # graph[2] = [1, 3]
  # graph[3] = [2, 4, 5]
  # graph[4] = [3]
  # graph[5] = [3]
  # optimal_touring.mst = graph
  # optimal_touring.generate_mst_tour(2)

  # print(optimal_touring.mst)
  # for visit_on_day in optimal_touring.generate_tour():
  #   print(*visit_on_day)

  for visit_on_day in optimal_touring.generate_mst_tour():
    print(*visit_on_day)
  
  end = timer()
  print("Time: {0} s".format(end - timer_start), file=sys.stderr)

if __name__ == '__main__':
  main()
