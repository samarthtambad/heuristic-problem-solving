
# https://github.com/nspektor/Ambulance-Pickup-Architecture

# https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/arefinsave

import pandas as pd

# df = pd.DataFrame(matrixA, columns= ["index", "x", "y", "time_to_live", "time_to_hospital"])

def routing_one_ambulance(df):
    df_new = df.sort_values(["time_to_live"]).reset_index()
    patients = []
    start, current_time, patient_4 = routing_for_4(df_new, 0)
    patients.append(patient_4)
    print(df)
    
    while(start < len(df)):
        start, current_time, patient_4 = routing_for_4(df_new.iloc[start:] ,current_time)
        patients.append(patient_4)
    
    return patients
        

def routing_for_4(df, current_time):
    patients = []
    patient1 = 0
    start = 0
    print("current_time", current_time)
    while patient1 < len(df):
        next_patient_distance = df.iloc[patient1]["time_to_hospital"] + 1
        time_to_hospital = df.iloc[patient1]["time_to_hospital"]
        time_to_live =  df.iloc[patient1]["time_to_live"]
        if current_time + next_patient_distance + time_to_hospital < time_to_live:
            patients.append(df.iloc[patient1]["id"])
            current_time = current_time + next_patient_distance
            current_location_x, current_location_y = df.iloc[patient1]["x"], df.iloc[patient1]["y"]
            start = patient1 + 1
            break
        patient1  = patient1 + 1
     
    
    patient2 = patient1 + 1
    
    while patient2 < len(df):
        next_patient_distance = abs(current_location_x - df.iloc[patient2]["x"]) + abs(current_location_y - df.iloc[patient2]["y"]) + 1
        time_to_hospital = df.iloc[patient2]["time_to_hospital"]
        time_to_live =  df.iloc[patient2]["time_to_live"]
        
        if current_time + next_patient_distance + time_to_hospital < min(time_to_live, df.iloc[patient1]["time_to_live"]):
            patients.append(df.iloc[patient2]["id"])
            current_time = current_time + next_patient_distance
            current_location_x, current_location_y = df.iloc[patient2]["x"], df.iloc[patient2]["y"]
            start = patient2 + 1
            break
        patient2 = patient2 + 1
    
    
    patient3 = patient2 + 1
    

    while patient3 < len(df):
        
        next_patient_distance = abs(current_location_x - df.iloc[patient3]["x"]) + abs(current_location_y - df.iloc[patient3]["y"]) + 1
        time_to_hospital = df.iloc[patient3]["time_to_hospital"]
        time_to_live =  df.iloc[patient3]["time_to_live"]
        
        if current_time + next_patient_distance + time_to_hospital < min(time_to_live, df.iloc[patient1]["time_to_live"], df.iloc[patient2]["time_to_live"]):
            patients.append(df.iloc[patient3]["id"])
            current_time = current_time + next_patient_distance
            current_location_x, current_location_y = df.iloc[patient3]["x"], df.iloc[patient3]["y"]
            start = patient3 + 1
            break
        patient3 = patient3 + 1
    
    patient4 = patient3 + 1
    

    while patient4 < len(df):
        
        next_patient_distance = abs(current_location_x - df.iloc[patient4]["x"]) + abs(current_location_y - df.iloc[patient4]["y"]) + 1
        time_to_hospital = df.iloc[patient4]["time_to_hospital"]
        time_to_live =  df.iloc[patient4]["time_to_live"]
        
        if current_time + next_patient_distance + time_to_hospital < \
        min(time_to_live,  df.iloc[patient1]["time_to_live"], df.iloc[patient2]["time_to_live"], df.iloc[patient3]["time_to_live"]):
            patients.append(df.iloc[patient4]["id"])
            start = patient4 + 1
            break
        patient4 = patient4 + 1
    
    current_time = current_time + next_patient_distance + time_to_hospital + 1
    

    return start, current_time, patients
        
        
        

        




