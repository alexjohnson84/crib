from __future__ import division
from os import listdir
from copy import deepcopy
from multiprocessing import Pool
import math
import random
import json
import re
from gameplay.cribplay import CribGame, find_legal_moves


def run_discard_model(hands):
    discards = []
    for hand in hands:
        discards.append(random.sample(hand, 2))
    return discards


def run_peg_model(status):
    """

    """
    #outline for model to be implemented
    hand = status['hands'][status['pegger']]
    count = status['peg_count']
    legal_moves = find_legal_moves(count, hand)
    if len(legal_moves) == 0:
        return ['GO']
    else:
        return random.choice(hand)

def run_dummy_game(n):
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
            response = run_discard_model(hands)
            status = cg.update(status, response)
        elif status['phase'] == 'Turn' or status['phase'] == 'Pegging':
            response = run_peg_model(status)
            status = cg.update(status, response)
        else:
            status = cg.update(status)
    game_log[rnd][status['phase']] = deepcopy(status)
    return game_log


def run_multiple_games(n):
    game_logs = {}
    file_count = 0
    for i in xrange(n):
        game_logs[str(i)] = run_dummy_game(i)
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


def run_multi_paras(batch_size=2000):
    batch_num = get_highest_file('data/logs')
    batch_data = run_para_games(batch_size)
    with open('data/logs/para_game_%s.txt' % (batch_num), 'wt') as pg:
        # pg.write(str(batch_data))
        json.dump(batch_data, pg)


if __name__ == "__main__":
    run_multi_paras()
    # run_dummy_game(2)
