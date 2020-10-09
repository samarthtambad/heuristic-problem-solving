#!/usr/bin/python3

import sys
import heapq
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter, defaultdict

from hospital import Hospital
from person import Person


class AmbulancePickup:
    def __init__(self, file_path):

        # parsed
        self.x_loc = []
        self.y_loc = []
        self.rescue_time = []
        self.num_ambulance_at_hospital = []

        self.persons = []
        self.hospitals = []

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

        for idx, (x, y) in enumerate(self.hospital_locations):
            hospital = Hospital(idx, x, y, self.num_ambulance_at_hospital[idx])
            self.hospitals.append(hospital)

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
            person = Person(person_idx, self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx])
            hospital_idx = cluster_map[cluster_num]
            person.assign_hospital(hospital_idx, self.hospital_locations[hospital_idx][0], self.hospital_locations[hospital_idx][1])
            self.persons.append(person)
            self.hospitals[hospital_idx].add_person(person)

        print(self.persons)
        print(self.hospitals)
        
        # for hospital_idx, persons in enumerate(self.cluster):
        #     self.generate_sub_clusters(persons, self.num_ambulance_at_hospital[hospital_idx])
        
        # self.find_routes()
    

    # def generate_routes_greedy(self):
    #     load_time_per_person = 1
    #     unload_time = 1
    #     result = []

    #     for hospital_idx, patients in enumerate(self.cluster):
    #         routes = self.find_routes(patients, self.num_ambulance_at_hospital[hospital_idx])
    #         print(routes)

    # def find_routes(self, patients, ambulances):
        

    # def find_routes(self):
    #     """
    #     patients - array of patients indexes
    #     num_ambulance - number of ambulances

    #     return:
    #     [
    #         [, , , ],
    #         [, , , ]
    #     ]
    #     """
    #     load_time_per_person = 1
    #     unload_time = 1
    #     result = []

    #     for hospital_idx, persons in enumerate(self.cluster):
    #         sub_cluster = self.generate_sub_clusters(persons, self.num_ambulance_at_hospital[hospital_idx])
            
    #         # print(sub_cluster)
    #         for ambulance_idx, patient_list in enumerate(sub_cluster):
    #             person_order = []
    #             for person_idx in patient_list:
    #                 person_order.append((person_idx, self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]))
    #             person_order.sort(key=lambda x: x[3])

    #             x, y = self.hospital_locations[hospital_idx]
    #             cur_x, cur_y = x, y
    #             cur_time, count, path = 0, 0, []
    #             for idx, px, py, max_time in person_order:
    #                 dist_cur_to_hospital = abs(x - cur_x) + abs(y - cur_y)  # current location to hospital location
    #                 if count == 4:
    #                     cur_time = cur_time + dist_cur_to_hospital + unload_time
    #                     cur_x, cur_y = x, y
    #                     count = 0
    #                     result.append(path)
    #                     path = []
                    
    #                 dist_to_person = abs(px - cur_x) + abs(py - cur_y)  # current location to person's location
    #                 dist_to_hospital = abs(px - x) + abs(py - y)        # person's location to hospital location
                    
    #                 estimated_time = cur_time + dist_to_person + load_time_per_person + dist_to_hospital + unload_time
    #                 is_valid = True
    #                 for person_idx in path:
    #                     if estimated_time > self.rescue_time[person_idx]:
    #                         is_valid = False
    #                         break

    #                 if is_valid and estimated_time <= max_time:
    #                     path.append(idx)
    #                     count += 1
    #                     cur_time = cur_time + dist_to_person + load_time_per_person
    #                     cur_x, cur_y = px, py
    #                 else:
    #                     cur_time = cur_time + dist_cur_to_hospital + unload_time
    #                     cur_x, cur_y = x, y
    #                     count = 0
    #                     result.append(path)
    #                     path = []
    #                     if cur_time + dist_to_hospital + load_time_per_person + dist_to_hospital + unload_time <= max_time:
    #                         path.append(idx)
    #                         count += 1
    #                         cur_time = cur_time + dist_to_person + load_time_per_person
    #                         cur_x, cur_y = px, py
    #                 # print(idx, x, y, max_time)
        
    #     print(result)



if __name__ == "__main__":
    input_file = sys.argv[1]
    print("input_file", input_file)

    game = AmbulancePickup(input_file)
