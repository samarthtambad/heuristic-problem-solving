#!/usr/bin/python3

import sys
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
import heapq
from itertools import permutations
import random


class AmbulancePickup:
    def __init__(self, file_path):

        # parsed
        self.x_loc = []
        self.y_loc = []
        self.rescue_time = []
        self.num_ambulance_at_hospital = []

        self.load_time_per_person = 1
        self.unload_time = 1

        # computed
        self.num_hospitals = 0
        self.hospital_locations = []
        self.cluster = []
        self.people_locations = np.empty((0,2), int)
        self.ambulances = None
        # self.cluster_map = np.array([])
        
        # result
        self.result = []

        # function calls
        self.read_input(file_path)
        # print(self.people_locations)
        self.assign_cluster()
        # self.print_input()
        # print(self.find_solution())
        self.generate_output()

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

        counter = Counter(kmeans.labels_)

        ambulances = []
        for i, (elem, _) in enumerate(counter.most_common()):
            count, _ = heapq.heappop(heap)
            count = -count
            x, y = self.hospital_locations[elem]
            for _ in range(count):
                ambulances.append([x, y, elem])
        
        self.ambulances = ambulances
        print(ambulances)

        # self.find_routes()

    def get_persons_savable(self, cur_selected, cur_time, cur_x, cur_y):
        savable = []
        load_time_per_person = 1
        unload_time = 1
        num_persons = len(self.x_loc)

        for person_idx in range(num_persons):
            x, y, rescue_time = self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]
            
            for hospital_idx in range(self.num_hospitals):
                hospital_x, hospital_y = self.hospital_locations[hospital_idx]

                time_cur_to_hospital = abs(hospital_x - cur_x) + abs(hospital_y - cur_y)  # current location to hospital location
                time_to_person = abs(x - cur_x) + abs(y - cur_y)                          # current location to person's location
                time_to_hospital = abs(x - hospital_x) + abs(y - hospital_y)              # person's location to hospital location

                estimated_time = cur_time + time_to_person + load_time_per_person + time_to_hospital + unload_time

                is_valid = True
                for idx in cur_selected:
                    if estimated_time > self.rescue_time[idx]:
                        is_valid = False
                        break
                
                if is_valid and estimated_time <= rescue_time:
                    savable.append((person_idx, hospital_idx))
                    break
        
        return savable

    def find_solution(self):
        result = []
        num_ambulance = len(self.ambulances)
        ambulances = [i for i in range(num_ambulance)]
        
        saved = set()

        for ambulance in ambulances:
            cur_time, cur_x, cur_y, start = 0, self.ambulances[ambulance][0], self.ambulances[ambulance][1], self.ambulances[ambulance][2]
            path, count = [start], 0
            end = None

            while True:
                savable = self.get_persons_savable(path, cur_time, cur_x, cur_y)

                if len(savable) == 0:
                    break

                found = False
                for person, hospital in savable:
                    if person not in saved:
                        found = True
                        saved.add(person)
                        path.append(person)
                        x, y = self.x_loc[person], self.y_loc[person]
                        hospital_x, hospital_y = self.hospital_locations[hospital]
                        time_to_person = abs(x - cur_x) + abs(y - cur_y)
                        cur_time = cur_time + time_to_person + self.load_time_per_person
                        cur_x, cur_y = x, y
                        
                        if len(path) == 4:
                            time_to_hospital = abs(cur_x - hospital_x) + abs(cur_y - hospital_y)
                            cur_time = cur_time + time_to_hospital + self.unload_time
                            cur_x, cur_y = hospital_x, hospital_y
                            path.append(hospital)
                            result.append(path)
                            path = [hospital]

                        end = hospital
                        break
                
                if not found:
                    break

            if len(path) > 0:
                path.append(end)
                result.append(path)
            
        return result

    def generate_output(self):
        with open("result", "w") as f:

            # print hospitals info
            for hospital_idx in range(self.num_hospitals):
                hospital_x, hospital_y = self.hospital_locations[hospital_idx]
                num_ambulance = self.num_ambulance_at_hospital[hospital_idx]
                print("Hospital: {0}, {1}, {2} ".format(hospital_x, hospital_y, num_ambulance), file=f)
            
            print("", file=f)

            # print path info
            result = self.find_solution()
            print(result)
            for path in result:
                start = path[0]
                hospital_x, hospital_y = self.hospital_locations[start]
                print("Ambulance: {0}: ({1},{2}), ".format(start+1, hospital_x, hospital_y), file=f, end='')

                for person_idx in path[1:-1]:
                    print("{0}: ({1},{2},{3}), ".format(person_idx+1, self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]), file=f, end='')

                end = path[-1]
                hospital_x, hospital_y = self.hospital_locations[end]
                print("{0}: ({1},{2})".format(end+1, hospital_x, hospital_y), file=f)


if __name__ == "__main__":
    input_file = sys.argv[1]
    print("input_file", input_file)

    game = AmbulancePickup(input_file)
