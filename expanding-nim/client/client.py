#!python3

import sys
from getopt import getopt
import requests
import time
import random


def create_session(base_url, player_name, init_stones):
    print("\nCreating a new session ... ", end='')
    payload = {
        "name": player_name,
        "stones": init_stones
    }
    r = requests.post("{}/sessions.json".format(base_url), data=payload)
    data = check_http_response(r)
    print("success\nSession ID: {}, Token: {}".format(data['session_id'], data['token']))
    return data['session_id'], data['token']
    
    
def join_session(base_url, session_id, player_name):
    print("\nJoining the session {} ... ".format(session_id), end='')
    payload = {
        "id": session_id,
        "name": player_name
    }
    r = requests.post("{}/sessions/join.json".format(base_url), data=payload)
    data = check_http_response(r)
    print("success\nToken: {}".format(data['token']))
    return data['token']
    
    
def session_status(base_url, session_id, token):
    print("\nChecking the session {} ... ".format(session_id), end='')
    r = requests.get("{}/sessions/{}/status.json?token={}".format(base_url, session_id, token))
    data = check_http_response(r)
    print("success")
    print(data["message"])
    return data
    

def make_move(base_url, session_id, token, auto_play, status):
    print("Stones Left:", status["stones_left"])
    print("Reset Imposed:", status["reset"])
    print("Current Max:", status["current_max"])
    print("Accept Value Range: [1-{}]".format(status["accept_max_value"]))
    print("Your Start Time:", status["start_time"])
    print("Your Time Left: {} s".format(status["time_left"]))
    print("Please enter how much stones you want to remove [1-{}]: ".format(status["accept_max_value"]), end='')
    
    
    dp_matrix = [[[[[None for k in range(2)] for j in range(5)] for i in range(5)]for a in range(50)]for u in range(1001)]
    num, reset = next_move(status["stones_left"], status["accept_max_value"], status["reset_left"], 4, 1, dp_matrix)   

    submit_move(base_url, session_id, token, num, reset)

def next_move(stones_left, current_max, my_reset_left, opponent_reset_left, game_condition, dp_matrix):
    stones_pick = 1
    #print("stones_left", stones_left)
    if stones_left <= current_max:
        if game_condition:
            stones_pick = stones_left
            dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition] = [stones_pick, "no"]
            return dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition]
        else:
            dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition] = ["Not_Possible", "no"]
            return dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition]
    
    elif stones_left == 4 and current_max < 4:
        if game_condition:
            dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition] = ["Not_Possible", "no"]
            return dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition]
        else:
            stones_pick = 3
            dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition] = [stones_pick, "no"]
            return dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition]
            
    else:
        i = current_max
        while (True and i >= 1):
            with_reset = None
            #print("game_condition", game_condition)
            if not dp_matrix[stones_left - i] [max(i+1, current_max)]  [opponent_reset_left] [my_reset_left] [not game_condition]:
                dp_matrix[stones_left - i] [max(i+1, current_max)]  [opponent_reset_left] [my_reset_left] [not game_condition] = next_move(stones_left - i, max(i+1, current_max),  opponent_reset_left, my_reset_left, not game_condition, dp_matrix)
            without_reset =  dp_matrix[stones_left - i] [max(i+1, current_max)]  [opponent_reset_left] [my_reset_left] [not game_condition][0]
            #print('without_reset', without_reset)
            if my_reset_left >= 1:
                if not dp_matrix[stones_left - i] [max(i+1, current_max)]  [opponent_reset_left] [my_reset_left-1] [not game_condition]:
                    dp_matrix[stones_left - i] [max(i+1, current_max)]  [opponent_reset_left] [my_reset_left-1] [not game_condition] = next_move(stones_left - i, max(i+1, current_max), opponent_reset_left, my_reset_left-1,  not game_condition, dp_matrix)
                with_reset  =  dp_matrix[stones_left - i] [max(i+1, current_max)]  [opponent_reset_left] [my_reset_left-1] [not game_condition][0]
                #print('with_reset', with_reset)
            if  without_reset != "Not_Possible":
                dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition] = [i,  "no"] 
                return dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition]
            elif with_reset and with_reset != "Not_Possible":
                dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition] = [i, "yes"]
                return dp_matrix[stones_left][current_max][my_reset_left] [opponent_reset_left] [game_condition]
            i -=1
        return "Not Possible"
    
    
def submit_move(base_url, session_id, token, stones, reset):
    print("\nSubbmitting ... ", end='')
    payload = {
        "stones": stones,
        "reset": reset
    }
    r = requests.post("{}/sessions/{}/move.json?token={}".format(base_url, session_id, token), data=payload)
    data = check_http_response(r)
    print("success")

    
def check_http_response(r):
    if r.status_code != requests.codes.ok:
        print('failed\nHTTP Request Returns ' + str(r.status_code))
        exit(-1)

    data = r.json()
    
    if data['status'] != 'success':
        print("failed\nHTTP Request Failed. Reason: " + data['reason'])
        exit(-1)
        
    return data
    

if __name__ == '__main__':
    player_name = None
    init_stones = None
    session_id = None
    auto_play = False
    base_url = "https://expanding-nim.iltc.app"
    token = None
    
    opts, args = getopt(sys.argv[1:], "", ["name=", "stones=", "id=", "url=", "auto"])

    for opt in opts:
        if opt[0] == "--name":
            player_name = opt[1]
            
        if opt[0] == "--stones":
            init_stones = int(opt[1])
            
        if opt[0] == "--id":
            session_id = int(opt[1])
            
        if opt[0] == "--url":
            base_url = opt[1]
            
        if opt[0] == "--auto":
            auto_play = True

    if player_name is None:
        print("Missing '--name'")
        exit(-1)
        
    if init_stones is None and session_id is None:
        print("Please provide '--stones' to create a new session or '--id' to join an existing session")
        exit(-1)
        
    if session_id is None:
        session_id, token = create_session(base_url, player_name, init_stones)
    else:
        token = join_session(base_url, session_id, player_name)
        
    while True:
        status = session_status(base_url, session_id, token)
        
        if status["game_status"] == "end":
            break
        
        if not status["your_turn"]:
            print("Will check again in 3 seconds ...")
            time.sleep(3)
        else:
            make_move(base_url, session_id, token, auto_play, status)
