from gameplay.cribplay import CribGame
import random
import json
from pprint import pprint
from copy import deepcopy

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

def run_dummy_game():
    cg = CribGame()
    rnd = 0
    peg_rnd = 0
    game_log = {rnd:{}}
    game_log[rnd]['Pegging'] = {}
    status = None
    status = cg.update(status)
    while status['phase'] != 'Game Over':
        if status['phase'] == 'Pegging':
            print status
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
    for i in xrange(n):
        game_logs[i] = run_dummy_game()
        # if i % 1000 == 0:
        #     print "processed %s of %i iterations" % (i, n)
    with open('data/game_logs.txt', 'wt') as gl:
        json.dump(game_logs, gl, indent=4)
if __name__ == "__main__":
    run_multiple_games(1)
    # run_dummy_game()
