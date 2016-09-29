from __future__ import division
from os import listdir
from copy import deepcopy
from multiprocessing import Pool
import math
import random
import json
import re
from gameplay.cribplay import CribGame, find_legal_moves, find_best_hand_combination, find_best_peg
import sys

def run_discard_model(status, rand):
    hands = status['hands']
    dealer = status['dealer']
    discards = []

    for i, hand in enumerate(hands):
        isdeal = i == dealer
        if rand == True:
            discards.append(random.sample(hand, 2))
        else:
            discards.append(find_best_hand_combination(hand, isdeal))
    return discards


def run_peg_model(status, rand):
    """

    """
    #outline for model to be implemented
    hand = status['hands'][status['pegger']]
    count = status['peg_count']
    legal_moves = find_legal_moves(count, hand)
    if len(legal_moves) == 0:
        return ['GO']
    else:
        if rand == True:
            return random.choice(hand)
        else:
            return find_best_peg(legal_moves, status)

def run_dummy_game(rand=True):
    cg = CribGame()
    rnd = 0
    peg_rnd = 0
    game_log = {rnd: {}}
    game_log[rnd]['Pegging'] = {}
    status = None
    status = cg.update(status)
    while status['phase'] != 'Game Over':
        if status['phase'] == 'Pegging':
            game_log[rnd][status['phase']][peg_rnd] = deepcopy(status)
            peg_rnd += 1
        else:
            game_log[rnd][status['phase']] = deepcopy(status)

        if status['phase'] == 'Round Complete':
            peg_rnd = 0
            rnd += 1
            game_log[rnd] = {}
            game_log[rnd]['Pegging'] = {}

        if status['phase'] == 'Deal':
            hands = status['hands']
            response = run_discard_model(status, rand)
            status = cg.update(status, response)
        elif status['phase'] == 'Turn' or status['phase'] == 'Pegging':
            response = run_peg_model(status, rand)
            status = cg.update(status, response)
        else:
            status = cg.update(status)
    game_log[rnd][status['phase']] = deepcopy(status)
    return game_log

def run_para_games(n, rand=True):
    p = Pool(16)
    data = p.map(run_dummy_game, [rand] * n)
    return data


def get_highest_file(base_dir):
    files = listdir(base_dir)
    if len(files) > 0:
        minimum_file = max([int(re.search(r'\d+', fil).group())
                            for fil in files]) + 1
    else:
        minimum_file = 0
    return minimum_file


def run_multi_paras(batch_size=2000, rand=True):
    if rand == True:
        base_dir = 'data/logs/random/'
    else:
        base_dir = 'data/logs/model/'
    batch_num = get_highest_file(base_dir)
    batch_data = run_para_games(batch_size)
    with open(base_dir + 'para_game_%s.txt' % (batch_num), 'wt') as pg:
        json.dump(batch_data, pg)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = bool(sys.argv[1])
    else:
        arg = False
    run_multi_paras(rand=arg)
