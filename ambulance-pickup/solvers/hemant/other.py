
# https://github.com/nspektor/Ambulance-Pickup-Architecture

# https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/arefinsave

import pandas as pd

df = pd.read_csv("/Users/hemantsingh/Downloads/heuristic-problem-solving/ambulance-pickup/solvers/hemant/ambulance1.csv")
#df = pd.DataFrame(matrixA, columns= ["index", "x", "y", "time_to_live", "time_to_hospital"])

def routing_one_ambulance(df):
    df_new = df.sort_values(["time_to_live"]).reset_index()[["index", "x", "y", "time_to_live", "time_to_hospital"]]
    print(df_new)
    patients = []
    df_rec, current_time, patient_4 = routing_for_4(df_new, 0)
    patients.append(patient_4)
    
    while(len(df_rec)) > 0 :
        df_rec, current_time, patient_4 = routing_for_4(df_rec ,current_time)
        if len(patient_4) == 0 : 
            break
        patients.append(patient_4)
    #print("patiensts....................", patients )
    return patients
        

def routing_for_4(df, current_time):
    patients = []
    patient1 = 0
    start = 0
    time_to_hospital_final = 0
    df_initial = df
    drop_ind = []
    
    while patient1 < len(df):
        next_patient_distance = df.iloc[patient1]["time_to_hospital"] + 1
        time_to_hospital = df.iloc[patient1]["time_to_hospital"] + 1
        time_to_live =  df.iloc[patient1]["time_to_live"]
        if current_time + next_patient_distance + time_to_hospital < time_to_live:
            
            patients.append(df.iloc[patient1]["index"])
            current_time = current_time + next_patient_distance
            current_location_x, current_location_y = df.iloc[patient1]["x"], df.iloc[patient1]["y"]
            start = patient1 + 1
            time_to_hospital_final = time_to_hospital
            drop_ind.append(patient1)
            break
        patient1  = patient1 + 1
     
    
    patient2 = patient1 + 1
    
    while patient2 < len(df):
        next_patient_distance = abs(current_location_x - df.iloc[patient2]["x"]) + abs(current_location_y - df.iloc[patient2]["y"]) + 1
        time_to_hospital = df.iloc[patient2]["time_to_hospital"] + 1
        time_to_live =  df.iloc[patient2]["time_to_live"]
        
        if current_time + next_patient_distance + time_to_hospital < min(time_to_live, df.iloc[patient1]["time_to_live"]):
            patients.append(df.iloc[patient2]["index"])
            current_time = current_time + next_patient_distance
            current_location_x, current_location_y = df.iloc[patient2]["x"], df.iloc[patient2]["y"]
            start = patient2 + 1
            time_to_hospital_final = time_to_hospital
            drop_ind.append(patient2)
            break
        patient2 = patient2 + 1
    
    
    patient3 = patient2 + 1
    

    while patient3 < len(df):
        
        next_patient_distance = abs(current_location_x - df.iloc[patient3]["x"]) + abs(current_location_y - df.iloc[patient3]["y"]) + 1
        time_to_hospital = df.iloc[patient3]["time_to_hospital"] + 1
        time_to_live =  df.iloc[patient3]["time_to_live"]
        
        if current_time + next_patient_distance + time_to_hospital < min(time_to_live, df.iloc[patient1]["time_to_live"], df.iloc[patient2]["time_to_live"]):
            patients.append(df.iloc[patient3]["index"])
            current_time = current_time + next_patient_distance
            current_location_x, current_location_y = df.iloc[patient3]["x"], df.iloc[patient3]["y"]
            start = patient3 + 1
            time_to_hospital_final = time_to_hospital
            drop_ind.append(patient3)
            break
        patient3 = patient3 + 1
    
    patient4 = patient3 + 1
    

    while patient4 < len(df):
        
        next_patient_distance = abs(current_location_x - df.iloc[patient4]["x"]) + abs(current_location_y - df.iloc[patient4]["y"]) + 1
        time_to_hospital = df.iloc[patient4]["time_to_hospital"]
        time_to_live =  df.iloc[patient4]["time_to_live"]
        
        if current_time + next_patient_distance + time_to_hospital < \
        min(time_to_live,  df.iloc[patient1]["time_to_live"], df.iloc[patient2]["time_to_live"], df.iloc[patient3]["time_to_live"]):
            patients.append(df.iloc[patient4]["index"])
            start = patient4 + 1
            current_time = current_time + next_patient_distance
            time_to_hospital_final = time_to_hospital
            drop_ind.append(patient4)
            break
        patient4 = patient4 + 1
    

    if len(patients) == 0:
        return df, current_time, patients

    else:
        df_initial = df.drop(drop_ind).reset_index()[["index", "x", "y", "time_to_live", "time_to_hospital"]]
        return df_initial, current_time + time_to_hospital_final, patients

        
        
print(routing_one_ambulance(df))
        




