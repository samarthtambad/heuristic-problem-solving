#!/usr/bin/python3

import sys
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
import heapq
from itertools import permutations
import random
from timeit import default_timer as timer

timer_start = timer()

class AmbulancePickup:

    def __init__(self, file_path):

        # parsed
        self.x_loc = []
        self.y_loc = []
        self.rescue_time = []
        self.num_ambulance_at_hospital = []

        self.load_time_per_person = 1
        self.unload_time = 1
        self.max_cpu_time = 5

        # computed
        self.num_hospitals = 0
        self.num_persons = 0
        self.hospital_locations = []
        self.cluster = []
        self.people_locations = np.empty((0,2), int)
        self.ambulances = None
        
        # result
        self.result = []

        # function calls
        self.read_input(file_path)
        self.assign_cluster()
        self.generate_output()

    def read_input(self, file_path):
        with open(file_path) as fp:
            state = 0
            for _, line in enumerate(fp):
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
                    else:
                        # hospital(numambulance)
                        state = 2
                elif state == 2:
                    # read number of ambulances at each hospital
                    ln = line.strip()
                    self.num_ambulance_at_hospital.append(int(ln))
        
        self.num_hospitals = len(self.num_ambulance_at_hospital)
        self.num_persons = len(self.x_loc)

    def print_input(self):
        n = len(self.x_loc)
       
        print("x_loc \t y_loc \t rescue_time")
        for i in range(n):
            print("{0} \t {1} \t {2}".format(self.x_loc[i], self.y_loc[i], self.rescue_time[i]))
        
        print("num_ambulance")
        for i in range(len(self.num_hospitals)):
            print(self.num_ambulance_at_hospital[i])

    def assign_cluster(self):
        kmeans = KMeans(n_clusters=self.num_hospitals, random_state=0).fit(self.people_locations)
        print(kmeans.labels_)
        
        # assign hospital locations
        hospital_locations = kmeans.cluster_centers_.astype(int)
        print(hospital_locations)

        hospital_locations_new = [None for _ in range(len(hospital_locations))]

        heap = []
        for i, count in enumerate(self.num_ambulance_at_hospital):
            heap.append((-count, i))
        heapq.heapify(heap)

        counter = Counter(kmeans.labels_)
        print(counter)
        for i, (hidx, _) in enumerate(counter.most_common()):
            _, new_idx = heapq.heappop(heap)
            hospital_locations_new[new_idx] = hospital_locations[hidx]
        self.hospital_locations = hospital_locations_new
        print(hospital_locations_new)

        ambulances = []
        for hospital_idx, count in enumerate(self.num_ambulance_at_hospital):
            x, y = self.hospital_locations[hospital_idx]
            for _ in range(count):
                ambulances.append([x, y, hospital_idx])
        
        self.ambulances = ambulances
        print(ambulances)

    def get_persons_savable(self, cur_selected, cur_time, cur_x, cur_y, allowed_destinations):
        savable = []
        load_time_per_person = 1
        unload_time = 1
        num_persons = len(self.x_loc)

        for person_idx in range(num_persons):
            x, y, rescue_time = self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]
            destinations = []
            
            for hospital_idx in allowed_destinations:
                hospital_x, hospital_y = self.hospital_locations[hospital_idx]

                time_to_person = abs(x - cur_x) + abs(y - cur_y)                          # current location to person's location
                time_to_hospital = abs(x - hospital_x) + abs(y - hospital_y)              # person's location to hospital location

                estimated_time = cur_time + time_to_person + load_time_per_person + time_to_hospital + unload_time

                is_valid = True
                for idx in cur_selected:
                    if estimated_time > self.rescue_time[idx]:
                        is_valid = False
                        break
                
                if is_valid and estimated_time <= rescue_time:
                    destinations.append(hospital_idx)
                    # savable.append((person_idx, hospital_idx))
        
            if len(destinations) > 0:
                savable.append((person_idx, destinations))

        return sorted(savable, key=lambda a: abs(self.x_loc[a[0]] - cur_x) + abs(self.y_loc[a[0]] - cur_y))

    def find_solution(self, ambulances):
        result = []
        
        saved = set()
        score = 0

        for ambulance_idx in ambulances:
            cur_time, cur_x, cur_y = 0, self.ambulances[ambulance_idx][0], self.ambulances[ambulance_idx][1]
            start, end, path = self.ambulances[ambulance_idx][2], self.ambulances[ambulance_idx][2], []   # index of hospital of ambulance
            destinations = [i for i in range(self.num_hospitals)]

            for _ in range(self.num_persons):

                found = False
                for person, destinations in self.get_persons_savable(path, cur_time, cur_x, cur_y, destinations):
                    hospital = destinations[0]
                    if person not in saved:
                        # print("Ambulance: {0}, Person: {1}, Destinations: {2}".format(ambulance_idx+1, person+1, destinations))
                        found = True
                        saved.add(person)
                        path.append(person)
                        score += 1
                        x, y = self.x_loc[person], self.y_loc[person]
                        hospital_x, hospital_y = self.hospital_locations[hospital]
                        time_to_person = abs(x - cur_x) + abs(y - cur_y)
                        cur_time = cur_time + time_to_person + self.load_time_per_person
                        cur_x, cur_y = x, y
                        end = hospital
                        
                        if len(path) == 4:
                            time_to_hospital = abs(cur_x - hospital_x) + abs(cur_y - hospital_y)
                            cur_time = cur_time + time_to_hospital + self.unload_time
                            cur_x, cur_y = hospital_x, hospital_y
                            # print("Ambulance: {0}, Start: {1}, Path: {2}, End: {3}".format(ambulance_idx+1, start+1, path, hospital+1))
                            result.append((start, end, path))
                            path, start = [], hospital
                        
                        break
                    
                if not found:
                    break

            if len(path) > 0:
                # print("Ambulance: {0}, Start: {1}, Path: {2}, End: {3}".format(ambulance_idx+1, start+1, path, end+1))
                result.append((start, end, path))
            
        return score, result

    def find_best_solution_permutations(self):
        ambulances_list = [i for i in range(len(self.ambulances))]

        max_score, best_result = 0, None
        for ambulances in permutations(ambulances_list):
            score, result = self.find_solution(ambulances)
            if score > max_score:
                max_score = score
                best_result = result
            if (timer() - timer_start) > 110:
                break

        return best_result
    
    def find_best_solution_two_opt(self):
        ambulances_list = [i for i in range(len(self.ambulances))]
        max_score, best_result = 0, None
        improved = True
      
        while improved:
            improved = False
            for i in range(len(ambulances_list)):
                if (timer() - timer_start) > self.max_cpu_time: break
                for j in range(i + 1, len(ambulances_list)):
                    if (timer() - timer_start) > self.max_cpu_time: break
                    if j - i == 0: continue
                    ambulances = self.swap_2opt(ambulances_list, i, j)
                    score, result  = self.find_solution(ambulances)
                    if score > max_score:
                        max_score = score
                        best_result = result
                        improved = True
        
        return best_result

    def swap_2opt(self, route, i, j):
      return route[:i] + route[i:j+1][::-1] + route[j+1:]

    def generate_output(self):
        with open("result", "w") as f:

            # print hospitals info
            for hospital_idx in range(self.num_hospitals):
                hospital_x, hospital_y = self.hospital_locations[hospital_idx]
                num_ambulance = self.num_ambulance_at_hospital[hospital_idx]
                print("Hospital: {0}, {1}, {2} ".format(hospital_x, hospital_y, num_ambulance), file=f)
            
            print("", file=f)

            # print path info
            result = self.find_best_solution_two_opt()
            # result.sort(key=lambda x: x[0])
            print(result)
            for start, end, path in result:
                hospital_x, hospital_y = self.hospital_locations[start]
                print("Ambulance: {0}: ({1},{2}), ".format(start+1, hospital_x, hospital_y), file=f, end='')

                for person_idx in path:
                    print("{0}: ({1},{2},{3}), ".format(person_idx+1, self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]), file=f, end='')

                hospital_x, hospital_y = self.hospital_locations[end]
                print("{0}: ({1},{2})".format(end+1, hospital_x, hospital_y), file=f)


if __name__ == "__main__":
    input_file = sys.argv[1]
    print("input_file", input_file)

    timer_start = timer()
    game = AmbulancePickup(input_file)
    timer_end = timer()
    print("Time: {0} s".format(timer_end - timer_start))
