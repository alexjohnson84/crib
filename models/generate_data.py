from gameplay.cribplay import CribGame
import random

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
    game_log = {}
    status = None
    status = cg.update(status)
    while status['phase'] != 'Round Complete':
        print status
        key = str(rnd) + str(status['phase'])
        game_log[key] = status
        if status['phase'] == 'Deal':
            hands = status['hands']
            response = run_discard_model(hands)
            status = cg.update(status, response)
        if status['phase'] == 'Turn' or status['phase'] == 'Pegging':
            hands = status['hands']
            response = run_peg_model(hands, status['pegger'], status['dealer'])
            status = cg.update(status,response)
        else:
            status = cg.update(status)
    key = str(rnd) + str(status['phase'])
    game_log[key] = status
    return game_log

def run_multiple_games(n):
    game_logs = {}
    for i in xrange(n):
        game_logs[i] = run_dummy_game()
        print i
    with open('data/game_logs.txt', 'wb') as gl:
        gl.write(str(game_logs))
if __name__ == "__main__":
    run_multiple_games(100)
    # run_dummy_game()
