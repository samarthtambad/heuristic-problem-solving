#!/usr/bin/python3

import sys
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
import heapq
from itertools import permutations
import pandas as pd

from other import routing_one_ambulance, routing_for_4

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


class AmbulancePickup:
    def __init__(self, file_path):

        # parsed
        self.x_loc = []
        self.y_loc = []
        self.rescue_time = []
        self.num_ambulance_at_hospital = []

        # computed
        self.num_hospitals = 0
        self.hospital_locations = []
        self.cluster = []
        self.people_locations = np.empty((0,2), int)
        # self.cluster_map = np.array([])
        
        # result
        self.result = []

        # function calls
        self.read_input(file_path)
        # print(self.people_locations)
        self.assign_cluster()
        # self.print_input()

    def read_input(self, file_path):
        with open(file_path) as fp:
            state = 0
            for cnt, line in enumerate(fp):
                if len(line.strip()) == 0:
                    continue
                if state == 0:
                    # person(xloc,yloc,rescuetime)
                    state = 1
                elif state == 1:
                    ln = line.strip().split(",")
                    if line[0].isdigit():
                        # read person's position and save time
                        self.x_loc.append(int(ln[0]))
                        self.y_loc.append(int(ln[1]))
                        self.rescue_time.append(int(ln[2]))
                        self.people_locations = np.append(self.people_locations, np.array([[int(ln[0]), int(ln[1])]]), axis=0)
                        # print("{0}".format(ln))
                    else:
                        # hospital(numambulance)
                        state = 2
                elif state == 2:
                    # read number of ambulances at each hospital
                    ln = line.strip()
                    self.num_ambulance_at_hospital.append(int(ln))
                    # print("{0}".format(ln))
        
        self.num_hospitals = len(self.num_ambulance_at_hospital)

    def print_input(self):
        n = len(self.x_loc)
       
        print("x_loc \t y_loc \t rescue_time")
        for i in range(n):
            print("{0} \t {1} \t {2}".format(self.x_loc[i], self.y_loc[i], self.rescue_time[i]))
        
        print("num_ambulance")
        for i in range(len(self.num_ambulance)):
            print(self.num_ambulance[i])

    def assign_cluster(self):
        kmeans = KMeans(n_clusters=self.num_hospitals, random_state=0).fit(self.people_locations)
        print(kmeans.labels_)
        
        # assign hospital locations
        self.hospital_locations = kmeans.cluster_centers_.astype(int)
        print(self.hospital_locations)

        # max-heap of number-of-ambulances with hospital index
        heap = []
        for i, count in enumerate(self.num_ambulance_at_hospital):
            heap.append((-count, i))
        heapq.heapify(heap)

        print(heap)

        cluster_map = {}
        counter = Counter(kmeans.labels_)
        print(counter)

        for i, (elem, count) in enumerate(counter.most_common()):
            count, hospital_idx = heapq.heappop(heap)
            print(-count, hospital_idx)
            cluster_map[elem] = hospital_idx
        
        print(cluster_map)
        
        self.cluster = [[] for _ in range(self.num_hospitals)]
        for person_idx, cluster_num in enumerate(kmeans.labels_):
            hospital_idx = cluster_map[cluster_num]
            self.cluster[hospital_idx].append(person_idx)

        print(self.cluster)
        
        # for hospital_idx, persons in enumerate(self.cluster):
        #     self.generate_sub_clusters(persons, self.num_ambulance_at_hospital[hospital_idx])
        
        self.find_routes()
    
    def generate_sub_clusters(self, persons, ambulances):
        locations = np.empty((0,2), int)
        for person_idx in persons:
            locations = np.append(locations, np.array([[self.x_loc[person_idx], self.y_loc[person_idx]]]), axis=0)
        
        kmeans = KMeans(n_clusters=ambulances, random_state=0).fit(locations)

        sub_cluster = [[] for _ in range(ambulances)]
        for idx, sub_cluster_num in enumerate(kmeans.labels_):
            person_idx = persons[idx]
            sub_cluster[sub_cluster_num].append(person_idx)
        
        return sub_cluster


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

    def find_routes(self):
        """
        patients - array of patients indexes
        num_ambulance - number of ambulances

        return:
        [
            [, , , ],
            [, , , ]
        ]
        """
        load_time_per_person = 1
        unload_time = 1
        
        result = []

        for hospital_idx, persons in enumerate(self.cluster):
            sub_cluster = self.generate_sub_clusters(persons, self.num_ambulance_at_hospital[hospital_idx])
            
            # print(sub_cluster)
            for ambulance_idx, patient_list in enumerate(sub_cluster):
                person_order = []
                for person_idx in patient_list:
                    person_order.append((person_idx, self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]))
                person_order.sort(key=lambda x: x[3])

                x, y = self.hospital_locations[hospital_idx]
                # cur_x, cur_y = x, y
                # cur_time, count, path = 0, 0, []
                data = []
                for idx, px, py, max_time in person_order:
                    time_to_hospital = abs(px - x) + abs(py - y)
                    data.append([idx, px, py, max_time, time_to_hospital])

                df = pd.DataFrame(data, columns= ["index", "x", "y", "time_to_live", "time_to_hospital"])

                ans = routing_one_ambulance(df)

                print("data", df)
                print("ans", ans)
                input("press some key to continue")

                    # dist_cur_to_hospital = abs(x - cur_x) + abs(y - cur_y)  # current location to hospital location
                    # if count == 4:
                    #     cur_time = cur_time + dist_cur_to_hospital + unload_time
                    #     cur_x, cur_y = x, y
                    #     count = 0
                    
                    # dist_to_person = abs(px - cur_x) + abs(py - cur_y)  # current location to person's location
                    # dist_to_hospital = abs(px - x) + abs(py - y)        # person's location to hospital location
                    
                    # if (cur_time + dist_to_person + load_time_per_person + dist_to_hospital + unload_time) <= max_time:
                    #     path.append(idx)
                    #     count += 1
                    #     cur_time = cur_time + dist_to_person + load_time_per_person
                    # else:
                    #     cur_time
                    # print(idx, x, y, max_time)

    # def find_routes_for_hospital(self, hospital_idx):
    #     patients = self.cluster[hospital_idx]
    #     ambulances = self.num_ambulance_at_hospital[hospital_idx]
    #     mst = self.generate_mst(patients)
        
    #     max_count = 0
    #     for vert in patients:
    #         path = self.get_mst_path(mst, vert)
    #         time, count, idx, available = 0, 0, 0, ambulances

    def generate_output(self):
        pass


if __name__ == "__main__":
    input_file = sys.argv[1]
    print("input_file", input_file)

    game = AmbulancePickup(input_file)
