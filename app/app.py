from flask import Flask, session, render_template, url_for, request, redirect
from gameplay.cribplay import CribGame, find_legal_moves
from copy import deepcopy
from forms import ResponseForm
from itertools import combinations
from sklearn.externals import joblib
import random


instructions = {'Deal': {'cue': 'Discard 2 Cards',
                        'selection': 2},
                'Discard': {'cue': 'Turn Over Card',
                            'selection': 0},
                'Turn': {'cue': 'Submit to Start Pegging',
                        'selection': 0},
                'Pegging': {'cue': 'Continue Pegging',
                            'selection': 1},
                'Pegging Complete': {'cue': 'Click to Score',
                'selection': 0},
                'Round Complete': {'cue': 'Click to Score',
                'selection': 0}
                }

app = Flask(__name__, static_url_path='/app/static')
app.config.from_object('config')

hand_model = joblib.load('models/hand_model/test_model.pkl')

with open('app/static/mapping/card_dir.txt') as f:
    img_map = eval(f.read())

def lookup_cards(lst):
    card_paths = []
    for card in lst:
        card_paths.append([card, url_for('static', filename=img_map[card])])
    return card_paths

def find_best_combination(hand, is_dealer):
    combos = combinations(hand, 4)
    max_score = 0
    max_combo = None
    for combo in combos:
        combo = list(combo) + [str(bool(is_dealer))]
        hand_dict = [{key:1 for key in combo}]
        predicted_val = hand_model.predict(hand_dict)
        if predicted_val > max_score:
            max_score = predicted_val
            max_combo = combo
    return [card for card in hand if card not in max_combo]

cg = CribGame()

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    session['legal_moves'] = 'null'
    if request.method == 'POST':
        session['discard_selection'] = request.values['discard_selection']
        return redirect(url_for('index'))
    obscure_hand = True
    # check for existence
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

    elif session['true_status']['phase'] in ['Pegging', 'Turn']:
        if session['true_status']['pegger'] == 0:
            user_response = session['discard_selection']
            session['true_status'] = cg.update(session['true_status'], user_response)

        opp_legal_moves = find_legal_moves(session['true_status']['peg_count'],
                                            session['true_status']['hands'][1]
                                            )
        if len(opp_legal_moves) == 0:
            opponent_response = ['GO']
        else:
            opponent_response = random.choice(opp_legal_moves)
        session['true_status'] = cg.update(session['true_status'], opponent_response)
        #user go
        session['legal_moves'] = find_legal_moves(session['true_status']['peg_count'],
                                        session['true_status']['hands'][0]
                                        )
        # run go automatically
        print 'legal_moves are %s' % (session['legal_moves'])
        if session['legal_moves'] == []:
            session['true_status'] = cg.update(session['true_status'], ['GO'])
    elif session['true_status']['phase'] == 'Pegging Complete':
        session['true_status'] = cg.update(session['true_status'])
        obscure_hand = False
    elif session['true_status']['phase'] == 'Round Complete':
        session['true_status'] = cg.update(session['true_status'])
        obscure_hand = False


    game_status = deepcopy(session['true_status'])
    if obscure_hand == True:
        game_status['hands'][1] = ["BB"] * len(game_status['hands'][1])
    if session['true_status']['faceup'] is not None:
        game_status['faceup'] = lookup_cards([game_status['faceup']])
    if session['true_status']['phase'] == 'Round Complete':
        #we render kitty where phist is for dealer
        dealer = game_status['dealer']
        game_status['peg_phist'][str(dealer)] = game_status['kitty']

    game_status['hands'] = [lookup_cards(hand) for hand in game_status['hands']]
    game_status['peg_phist'] = {key:lookup_cards(val) for key,val in game_status['peg_phist'].iteritems()}
    session['game_status'] = game_status
    form = ResponseForm()
    return redirect(url_for('crib'))

@app.route('/crib', methods=['GET'])
def crib():
    form = ResponseForm()
    discard_rounds = ['Deal', 'Turn', 'Pegging']
    if session['game_status']['phase'] in discard_rounds:
        c_class = 'discard'
    else:
        c_class = ''

    return render_template('index.html',  game_status=session['game_status'],
                            true_status=session['true_status'],
                            form=form,
                            cue=instructions[session['game_status']['phase']],
                            card_class=c_class,
                            legal_moves=session['legal_moves'])

@app.route('/reset', methods=['GET'])
def reset():
    session.clear()
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)

	# 'Deal': {
	# 	'peg_count': 0,
	# 	'deck': ['QD', 'JS', 'QH', '5H', '4H', '6H', 'AS', 'AC', '7C', '4C', '8H', '7H', '6S', '9H', '7S', '8S', 'QC', '2S', 'AD', 'KD', '4S', '5C', '10S', '7D', 'KH', 'JD', 'QS', 'KC', '9D', '3H', '2H', '9S', '10D', '3S', '8D', '5S', 'JH', '6C', 'JC', '4D'],
	# 	'hands': [
	# 		['6D', '3D', '9C', '5D', '2C', '10H'],
	# 		['2D', '8C', '3C', '10C', 'KS', 'AH']
	# 	],
	# 	'kitty': [],
	# 	'peg_phist': {
	# 		0: [],
	# 		1: []
	# 	},
	# 	'scores': [0, 0],
	# 	'phase': 'Deal',
	# 	'dealer': 0,
	# 	'faceup': None,
	# 	'pegger': None,
	# 	'peg_hist': []
	# },
