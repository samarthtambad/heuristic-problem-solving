#!python3

import sys
from getopt import getopt
import requests
import time
import random
from functools import lru_cache

opponent_reset = 4
winning_base_states = set([1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15])
losing_base_states = set([4, 8, 12, 16])

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
    

def calc_winning_moves(stones, current_max, is_player):

    @lru_cache(None)
    def helper(stones, current_max, is_player):
        res = 0
        if is_player:
            if stones in winning_base_states:
                return 1
            if stones in losing_base_states:
                return -1
            for i in range(1, current_max+1):
                res += helper(stones-i, current_max if i < current_max else current_max+1, not is_player)
        else:
            if stones in winning_base_states:
                return -1
            if stones in losing_base_states:
                return 1
            for i in range(1, current_max+1):
                res += helper(stones-i, current_max if i < current_max else current_max+1, not is_player)
        return res
    
    return helper(stones, current_max, is_player)


def make_move(base_url, session_id, token, auto_play, status):
    print("Stones Left:", status["stones_left"])
    print("Reset Imposed:", status["reset"])
    print("Current Max:", status["current_max"])
    print("Accept Value Range: [1-{}]".format(status["accept_max_value"]))
    print("Your Start Time:", status["start_time"])
    print("Your Time Left: {} s".format(status["time_left"]))
    print("Please enter how much stones you want to remove [1-{}]: ".format(status["accept_max_value"]), end='')

    stones = status["stones_left"]
    # reset = True if status["reset"] == "yes" else False
    # current_max = status["current_max"]
    accept_max_value = status["accept_max_value"]
    ans = None
    impose_reset = "no"
    
    # check if opponent can be forced to losing base state
    for i in range(1, accept_max_value+1):
        if (stones - i) in losing_base_states:
            ans = i
            impose_reset = "yes"
            break
    
    if ans is None:
        ans = random.randint(1, accept_max_value)
        
    submit_move(base_url, session_id, token, ans, impose_reset)
    
    
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
    n = int(sys.argv[1])
    current_max = int(sys.argv[2])
    print("n: {0}, current_max: {1}".format(n, current_max))
    for i in range(1, current_max+1):
        print("remove: {0}, stones: {1}, score: {2}".format(i, n-i, calc_winning_moves(n-i, current_max, False)))

"""
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
"""