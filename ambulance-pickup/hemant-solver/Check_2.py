import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from other import routing_one_ambulance, routing_for_4

import heapq
from collections import Counter, defaultdict

def plot_cluster(df, number_cluster):

    kmeans = KMeans(n_clusters= number_cluster)
    kmeans.fit(df[['x', 'y']])
    x = df["x"]
    y = df["y"]
    Cluster = kmeans.labels_

    df["cluster"] = kmeans.labels_
    return df

def hemant_solver(df, number_of_hospital, num_ambulance_at_hospital):

    kmeans = KMeans(n_clusters= number_of_hospital)
    kmeans.fit(df[['x', 'y']])
    df["cluster"] = kmeans.labels_
    cluster_locations = kmeans.cluster_centers_.astype(int)


    heap = []
    for i, count in enumerate(num_ambulance_at_hospital):
        heap.append((-count, i))
    heapq.heapify(heap)


    cluster_map = {}
    counter = Counter(kmeans.labels_)

    for i, (elem, count) in enumerate(counter.most_common()):
        count, hospital_idx = heapq.heappop(heap)
        print(-count, hospital_idx)
        cluster_map[elem] = hospital_idx

    print(cluster_map)

    hospital_number = []
    for cluster_num in kmeans.labels_:
        hospital_idx = cluster_map[cluster_num]
        hospital_number.append(hospital_idx)
    df["hospital_number"] = hospital_number

    patients_picked = []
    am_number = 0
    total_patients_picked = []
    for cluster_num in range(number_of_hospital):

        hospital_number = cluster_map[cluster_num]

        df_hospital = df.loc[df['hospital_number'] == hospital_number]
        hospital_location = cluster_locations[cluster_num]
        hospital_total_ambulance = num_ambulance_at_hospital[hospital_number]

        df_hospital = plot_cluster(df_hospital, hospital_total_ambulance)

        df_hospital["time_to_hospital"] = abs(df_hospital["x"] - hospital_location[0]) + abs(df_hospital["y"]-hospital_location[1])
        
        for ambulance_no in range(hospital_total_ambulance):
            df_ambulance = df_hospital.loc[df_hospital['cluster'] == ambulance_no]
            df_ambulance["index"] = df_ambulance.index
            #print("printing for the ambulance", am_number)
            
            #df_ambulance.to_csv(str(am_number) + ".csv", index = False)
            #print(routing_one_ambulance(df_ambulance))
            num, patient_per_ambulance = routing_one_ambulance(df_ambulance)
            
            for one_round_patients in patient_per_ambulance:
                print("one_round_patients",one_round_patients)
                start = hospital_number
                end = hospital_number
                array = (start, end, one_round_patients)
                patients_picked.append(array)
                
            
            #print(num)
            #total_patients_picked = total_patients_picked + num
            am_number = am_number + 1 
    print(patients_picked)
    return(patients_picked)

df = pd.read_csv("sample1.csv")
number_of_hospital, num_ambulance_at_hospital  =  5, [6,5,5,4,3, 3]

# 


with open("result", "w") as f:

    # print hospitals info
    for hospital_idx in range(number_of_hospital):
        hospital_x, hospital_y = hospital_locations[hospital_idx]
        num_ambulance = self.num_ambulance_at_hospital[hospital_idx]
        print("Hospital: {0}, {1}, {2} ".format(hospital_x, hospital_y, num_ambulance), file=f)
    
    print("", file=f)

    # print path info
    # result = self.find_solution() 
    result = hemant_solver(df, number_of_hospital, num_ambulance_at_hospital)
    print(result)
    # result.sort(key=lambda x: x[0])
    print(result)
    for start, end, path in result:
        hospital_x, hospital_y = self.hospital_locations[start]
        print("Ambulance: {0}: ({1},{2}), ".format(start+1, hospital_x, hospital_y), file=f, end='')

        for person_idx in path:
            print("{0}: ({1},{2},{3}), ".format(person_idx+1, self.x_loc[person_idx], self.y_loc[person_idx], self.rescue_time[person_idx]), file=f, end='')

        hospital_x, hospital_y = self.hospital_locations[end]
        print("{0}: ({1},{2})".format(end+1, hospital_x, hospital_y), file=f)