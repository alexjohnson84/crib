import numpy as np
from flask import Flask, session, render_template, url_for, request, redirect
from gameplay.cribplay import CribGame, find_legal_moves
from gameplay.cribbage_scoring import CribPegScore
from copy import deepcopy
from forms import ResponseForm
from itertools import combinations
from sklearn.externals import joblib
import random
import datetime
from pprint import pprint

instructions = {'Deal': {'cue': 'Discard 2 Cards',
                        'selection': 2},
                'Discard': {'cue': 'Turn Over Card',
                            'selection': 0},
                'Turn': {'cue': 'Submit to Start Pegging',
                        'selection': 1},
                'Pegging': {'cue': 'Continue Pegging',
                            'selection': 1},
                'Pegging Complete': {'cue': 'Click to Score',
                'selection': 0},
                'Round Complete': {'cue': 'Click to Score',
                'selection': 0}
                }

app = Flask(__name__, static_url_path='/app/static')
app.config.from_object('config')

hand_model = joblib.load('models/hand_model/model.pkl')
peg_model = joblib.load('models/peg_model/model.pkl')

with open('app/static/mapping/card_dir.txt') as f:
    img_map = eval(f.read())

def lookup_cards(lst):
    card_paths = []
    for card in lst:
        card_paths.append([card, url_for('static', filename=img_map[card])])
    return card_paths

def find_best_combination(hand, is_dealer):
    combos = [[str(list(combo)), is_dealer] for combo in combinations(hand, 4)]
    preds = hand_model.predict(combos)
    best_pred_hand = eval(combos[np.argmax(preds)][0])
    discards = [card for card in hand if card not in best_pred_hand]
    return discards

def find_best_peg(legal_moves, status):
    max_pred_points = 0
    best_move = legal_moves[0]
    for move in legal_moves:
        feats = extract_peg_features(status, move)
        pred_points = peg_model.predict([feats])
        if pred_points > max_pred_points:
            max_pred_points = pred_points
            best_move = move
    return best_move



def extract_peg_features(status, move):
    # import pdb; pdb.set_trace()
    player = status['pegger']
    hand = deepcopy(status['hands'][player]).remove(move)
    hist = status['peg_hist'] + [move]
    len_opponent = len(status['hands'][abs(player-1)])
    cps = CribPegScore(hist)
    count = cps.count
    return [hand, len(hist), hist, len_opponent, count]


def add_to_history(save=False):
    if 'history' in session:
        if 'discard_selection' in session:
            discard_selection = session['discard_selection']
        else:
            discard_selection = []
        session['history'].append((session['true_status'],
                                    datetime.datetime.now(),
                                    discard_selection))
    else:
        session['history'] = []
    if save == True:
        with open('data/user_logs.txt', 'a') as ul:
            ul.write(str(session['history']))

def get_opponent_response(status):
        opp_legal_moves = find_legal_moves(status['peg_count'],
                                            status['hands'][1]
                                            )
        if len(opp_legal_moves) == 0:
            opponent_response = ['GO']
        else:
            opponent_response = find_best_peg(opp_legal_moves, status)
        return opponent_response


cg = CribGame()


@app.route('/index', methods=['GET', 'POST'])
def index():
    session['legal_moves'] = 'null'
    if request.method == 'POST':
        session['discard_selection'] = request.values['discard_selection']
        return redirect(url_for('index'))
    obscure_hand = True
    save = False
    # check for existence
    # import pdb; pdb.set_trace()
    if 'true_status' not in session:
        session['true_status'] = cg.update()
    elif session['true_status']['phase'] == 'Deal':
        if 'discard_selection' in session:
            # import pdb; pdb.set_trace()
            user_response = session['discard_selection'].split(',')
            opponent_response = find_best_combination(session['true_status']['hands'][1], session['true_status']['dealer'])
            session['true_status'] = cg.update(session['true_status'], [user_response, opponent_response])
    elif session['true_status']['phase'] == 'Discard':
        session['true_status'] = cg.update(session['true_status'])
        if session['true_status']['dealer'] == 0:
            instructions['Turn']['selection'] = 0
        else:
            instructions['Turn']['selection'] = 1

    elif session['true_status']['phase'] in ['Pegging', 'Turn']:
        if session['true_status']['pegger'] == 0:
            user_response = session['discard_selection']
            session['true_status'] = cg.update(session['true_status'], user_response)

        opponent_response = get_opponent_response(session['true_status'])
        session['true_status'] = cg.update(session['true_status'], opponent_response)
        #user go
        session['legal_moves'] = find_legal_moves(session['true_status']['peg_count'],
                                        session['true_status']['hands'][0]
                                        )
        # run go automatically
        #this needs to be a while loop
        while session['legal_moves'] == []:
            session['true_status'] = cg.update(session['true_status'], ['GO'])
            session['legal_moves'] = find_legal_moves(session['true_status']['peg_count'],
                                                        session['true_status']['hands'][0]
                                                        )
            opponent_response = get_opponent_response(session['true_status'])
            session['true_status'] = cg.update(session['true_status'], opponent_response)
            if sum([len(hand) for hand in session['true_status']['hands']]) <= 1:
                break
        if session['true_status']['phase'] == 'Pegging Complete':
            session['legal_moves'] = 'null'

        print "legal moves are ", session['legal_moves']

    elif session['true_status']['phase'] == 'Pegging Complete':
        session['legal_moves'] = 'null'
        print "legal moves PC", session['legal_moves']
        session['true_status'] = cg.update(session['true_status'])
        obscure_hand = False
    elif session['true_status']['phase'] == 'Round Complete':
        session['true_status'] = cg.update(session['true_status'])
        obscure_hand = False
        save = True


    game_status = deepcopy(session['true_status'])
    if obscure_hand == True:
        game_status['hands'][1] = ["BB"] * len(game_status['hands'][1])
    if session['true_status']['faceup'] is not None:
        game_status['faceup'] = lookup_cards([game_status['faceup']])
    else:
        game_status['faceup'] = lookup_cards(['BB'])
    if session['true_status']['phase'] == 'Round Complete':
        #we render kitty where phist is for dealer
        dealer = game_status['dealer']
        game_status['peg_phist'][str(dealer)] = game_status['kitty']

    game_status['hands'] = [lookup_cards(hand) for hand in game_status['hands']]
    game_status['peg_phist'] = {key:lookup_cards(val) for key,val in game_status['peg_phist'].iteritems()}
    session['game_status'] = game_status
    form = ResponseForm()
    add_to_history(save)
    return redirect(url_for('crib'))

@app.route('/')
@app.route('/crib', methods=['GET'])
def crib():
    form = ResponseForm()
    discard_rounds = ['Deal', 'Turn', 'Pegging']
    if 'game_status' in session:
        if session['game_status']['phase'] in discard_rounds:
            c_class = 'discard'
        else:
            c_class = ''
        with open('app/session_log.txt', 'w+') as f:
            f.write(str(session))
        return render_template('index.html',  game_status=session['game_status'],
                                true_status=session['true_status'],
                                form=form,
                                cue=instructions[session['game_status']['phase']],
                                card_class=c_class,
                                legal_moves=session['legal_moves'])
    else:
        return redirect(url_for('index'))

@app.route('/reset', methods=['GET'])
def reset():
    session.clear()
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
