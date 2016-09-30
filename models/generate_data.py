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


"""
Run artificial games.  This module has the option when called to either run
games randomly, or use the generated model stored in models/hand_model or
models/peg_model to generate artifical games.  Data is stored as logs in
data/logs
"""


def run_discard_model(status, rand):
    """
    Function to select which cards to discard at the discard phase of the game.
    If random, we randomly select from the hand cards to discard, else we
    run the find_best_hand_combination to determine cards to discard
    INPUT: status (dict from cribplay api), israndom (bool)
    OUTPUT: cards to discard per user in form [[x,x],[y,y]]
    """
    hands = status['hands']
    dealer = status['dealer']
    discards = []
    for i, hand in enumerate(hands):
        isdeal = i == dealer
        if rand:
            discards.append(random.sample(hand, 2))
        else:
            discards.append(find_best_hand_combination(hand, isdeal))
    return discards


def run_peg_model(status, rand):
    """
    Function to select which cards to play during each peg round
    If random, we randomly select from the peg card to discard, else we find
    the best peg using the current model
    INPUT: status (dict from cribplay api), israndom (bool)
    OUTPUT: card to play
    """
    hand = status['hands'][status['pegger']]
    count = status['peg_count']
    legal_moves = find_legal_moves(count, hand)
    if len(legal_moves) == 0:
        return ['GO']
    else:
        if rand:
            return random.choice(hand)
        else:
            return find_best_peg(legal_moves, status)


def run_dummy_game(rand=True):
    """
    Run a single dummy game
    INPUT: israndom (bool)
    OUTPUT: dict of game log
    """
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
    """
    Run multiple dummy games in parallel using multiprocessing
    INPUT: number of games (int), isrand (bool)
    OUTPUT: list of game logs from run_dummy_game
    """
    p = Pool(16)
    data = p.map(run_dummy_game, [rand] * n)
    return data


def get_highest_file(base_dir):
    """
    Search active directory and find the highest number of file from the current
    directory. Used when generating new logs.
    INPUT: base directory
    OUTPUT: integer of the highest file number + 1.
    """
    files = listdir(base_dir)
    if len(files) > 0:
        minimum_file = max([int(re.search(r'\d+', fil).group())
                            for fil in files]) + 1
    else:
        minimum_file = 0
    return minimum_file


def run_multi_paras(batch_size=2000, rand=True):
    """
    Run multiple parallel games of specific batch size.  Json dump each game of
    specific batch size into a single file.

    Called in makefile as:
    seq 100 | xargs -Iz python models/generate_data.py True

    INPUT: Number of games to be run (int), isrand(bool)
    OUTPUT: None

    """
    if rand:
        base_dir = 'data/logs/random/'
    else:
        base_dir = 'data/logs/model/'
    batch_num = get_highest_file(base_dir)
    batch_data = run_para_games(batch_size)
    with open(base_dir + 'para_game_%s.txt' % (batch_num), 'w') as pg:
        json.dump(batch_data, pg)


if __name__ == "__main__":
    """
    Read in if any sysargvs have been called.  If sysargv is true,
    we generate random data, else we load in the models
    """
    if len(sys.argv) > 1:
        arg = bool(sys.argv[1])
    else:
        arg = False
    run_multi_paras(rand=arg)
