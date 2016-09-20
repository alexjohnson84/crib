from __future__ import division
import math
from gameplay.cribplay import CribGame
import random
import json
from copy import deepcopy
from multiprocessing import Pool
from os import listdir
import re

def run_discard_model(hands):
    discards = []
    for hand in hands:
        discards.append(random.sample(hand, 2))
    return discards

def run_peg_model(hands, pegger, dealer):
    """
    Run model for the player that's going to go next.
    In the beginning of the pegging method, players switch, so we run the model
    for the next player.
    """
    if pegger == None:
        player = abs(dealer-1)
    else:
        player = abs(pegger - 1)
    if len(hands[player]) == 0:
        return None
    return random.choice(hands[player])

def run_dummy_game(_):
    cg = CribGame()
    rnd = 0
    peg_rnd = 0
    game_log = {rnd:{}}
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
            response = run_discard_model(hands)
            status = cg.update(status, response)
        elif status['phase'] == 'Turn' or status['phase'] == 'Pegging':
            hands = status['hands']
            response = run_peg_model(hands, status['pegger'], status['dealer'])
            status = cg.update(status,response)
        else:
            status = cg.update(status)
    game_log[rnd][status['phase']] = deepcopy(status)
    return game_log

def run_multiple_games(n):
    game_logs = {}
    file_count = 0
    for i in xrange(n):
        game_logs[i] = run_dummy_game(i)
        if i % 1000 == 0:
            print "processed %s of %i iterations" % (i, n)
        if i % 10000 == 0:
            print "writing to file"
        with open('data/game_logs_%s.txt' % (file_count), 'wt') as gl:
            json.dump(game_logs, gl, indent=4)
            game_logs = {}
            file_count += 0

def run_para_games(n):
    p = Pool(16)
    data = p.map(run_dummy_game, range(n))
    return data

def get_highest_file(base_dir):
    files = listdir(base_dir)
    if len(files) > 0:
        minimum_file = max([int(re.search(r'\d+', fil).group())
                            for fil in files]) + 1
    else:
        minimum_file = 0
    return minimum_file

def run_multi_paras(batch_size=1):
    batch_num = get_highest_file('data/logs')
    batch_data = run_para_games(batch_size)
    with open('data/logs/test_para_game_%s.txt' % (batch_num), 'wt') as pg:
        pg.write(str(batch_data))







if __name__ == "__main__":
    run_multi_paras()
    # run_para_games(1000)
    # run_multiple_games(100000)
    # run_dummy_game()
