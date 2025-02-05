import json
import math
import random
import socket
import sys
import time
import copy

DATA_SIZE = 4096


def area(r1, r2, d):
    if r1 <= 0 or r2 <= 0:
        return 0
    if r1 + r2 < d:
        return 0
    if r1 + d < r2:
        return math.pi * r1 ** 2
    if r2 + d < r1:
        return math.pi * r2 ** 2
    return r1 ** 2 * math.acos((d ** 2 + r1 ** 2 - r2 ** 2) / (2 * d * r1)) + \
        r2 ** 2 * math.acos((d ** 2 - r1 ** 2 + r2 ** 2) / (2 * d * r2)) - \
        ((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2)) ** 0.5 / 2


def circum(r11, r12, r21, r22, d):
    return area(r12, r22, d) - area(r12, r21, d) - area(r11, r22, d) + area(r11, r21, d)


def taken(attachment, prior, d, rope):
    lower = max([i for i in prior if i <= attachment] or [0])
    higher = min([i for i in prior if i >= attachment] or [rope])
    return circum(lower, attachment, rope - higher, rope - attachment, d)


def get_socket(s, timed=False, time_limit=None):
    t0 = time.time()
    while True:
        data = s.recv(DATA_SIZE).decode('utf-8')
        if data:
            if timed:
                return data, time.time() - t0, True
            else:
                return data
        if timed and time.time() - t0 >= time_limit:
            return None, time_limit, False
        time.sleep(0.01)


def send_socket(s, data):
    s.sendall(data.encode('utf-8'))


def next_move(attachments_per_player, prior_moves, d, rope):
    # return next_move_random(prior_moves, d, rope)
    return next_move_greedy(prior_moves, d, rope)
    # return next_move_minimax(attachments_per_player, prior_moves, d, rope)
    # return next_move_backtrack(attachments_per_player, prior_moves, d, rope)


def next_move_random(prior_moves, d, rope):
    tries = 10
    move = max([random.random() * rope for _ in range(tries)], key=lambda x: taken(x, prior_moves, d, rope))
    return move


def next_move_greedy(prior_moves, d, rope):
    best_move, best_score = 0, 0
    for i in range(int(rope)+1):
        score = taken(i, prior_moves, d, rope)
        if score > best_score:
            best_score = score
            best_move = i
    return best_move


def get_possible_moves(prior_moves, d, rope):
    moves = []
    for i in range(int(rope)+1):
        score = taken(i, prior_moves, d, rope)
        moves.append((i, score))
    moves.sort(key=lambda x: x[1], reverse=True)
    return moves


def next_move_minimax(attachments_per_player, prior_moves, d, rope):

    def minimax(moves, total_score, depth, alpha, beta, maximizingPlayer):
        
        if depth == max_depth:
            return total_score, moves
        
        if maximizingPlayer:
            max_score, best_moves = float('-inf'), []
            possible_moves = get_possible_moves(moves, d, rope)
            # print(possible_moves)
            for i in range(branching_factor):
                cur_move, s = possible_moves[i]
                moves.append(cur_move)
                score, m = minimax(moves, total_score + s, depth + 1, alpha, beta, False)
                if score > max_score:
                    max_score = score
                    best_moves = m
                # update the upper bound
                # alpha = max(alpha, score)
                # if alpha >= beta:
                #     break
            return max_score, best_moves
        else:
            min_score, best_moves = float('inf'), []
            possible_moves = get_possible_moves(moves, d, rope)
            for i in range(branching_factor):
                cur_move, s = possible_moves[i]
                moves.append(cur_move)
                score, m = minimax(moves, total_score + s, depth + 1, alpha, beta, True)
                if score < min_score:
                    min_score = score
                    best_moves = m
                # beta = min(beta, score)
                # if alpha >= beta:
                #     break
            return min_score, best_moves

    max_depth = (2 * attachments_per_player) - len(prior_moves)
    branching_factor = 4
    m = copy.deepcopy(prior_moves)
    idx = len(m)
    best_score, moves = minimax(m, 0, 0, float('-inf'), float('inf'), True)
    print("Best Possible Score: {2}, Move: {1}".format(best_score, moves[idx]))
    return moves[idx]

def next_move_backtrack(attachments_per_player, prior_moves, d, rope):

    def backtrack(moves, player_score, opponent_score, depth, player):
        nonlocal max_score_diff
        nonlocal best_moves
        nonlocal max_depth
        
        if depth == max_depth:
            score_diff = (player_score - opponent_score)
            if score_diff > max_score_diff:
                max_score_diff = score_diff
                best_moves = copy.deepcopy(moves)
            return
        
        if player:
            possible_moves = get_possible_moves(moves, d, rope)
            for i in range(branching_factor):
                cur_move, move_score = possible_moves[i]
                moves.append(cur_move)
                backtrack(moves, player_score + move_score, opponent_score, depth + 1, False)
                moves.pop()
        else:
            possible_moves = get_possible_moves(moves, d, rope)
            for i in range(branching_factor):
                cur_move, move_score = possible_moves[i]
                moves.append(cur_move)
                backtrack(moves, player_score, opponent_score + move_score, depth + 1, False)
                moves.pop()

    max_score_diff, best_moves = float('-inf'), []
    max_depth = 4 # (2 * attachments_per_player) - len(prior_moves)
    branching_factor = 2
    m = copy.deepcopy(prior_moves)
    idx = len(m)
    backtrack(m, 0, 0, 0, True)
    print("Max Score Diff: {0}, Move: {1}".format(max_score_diff, best_moves[idx]))
    return best_moves[idx]


def run(d, rope, attachments_per_player, tries, site, name, player_order):
    HOST = site.split(':')[0]
    PORT = int(site.split(':')[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    send_socket(s, f'{player_order} {name}')
    for i in range(2 * attachments_per_player):
        moves = json.loads(get_socket(s))['moves']
        move = next_move(attachments_per_player, moves, d, rope)
        send_socket(s, str(move))


def get_argv(x):
    return sys.argv[sys.argv.index(x) + 1]


if __name__ == '__main__':

    run(float(get_argv('--dist')), float(get_argv('--rope')), int(get_argv('--turns')), int(get_argv('--tries')), get_argv('--site'), get_argv('--name'), 1 if '-f' in sys.argv else 2)
