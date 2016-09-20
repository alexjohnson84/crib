from flask import Flask, session, render_template, url_for, request
from gameplay.cribplay import CribGame
from copy import deepcopy
from forms import ResponseForm
from itertools import combinations
from sklearn.externals import joblib

app = Flask(__name__, static_url_path='/app/static')
app.config.from_object('config')

hand_model = joblib.load('models/hand_model/test_model.pkl')

with open('app/static/mapping/card_dir.txt') as f:
    img_map = eval(f.read())

def lookup_cards(lst):
    card_paths = []
    print lst
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
    if request.method == 'POST':
        if 'discard_selection' in request.values:
            user_reponse = request.values['discard_selection'].split(',')
            opponent_response = find_best_combination(session['true_status']['hands'][1], session['true_status']['dealer'])
            print opponent_response

            session['true_status'] = cg.update(session['true_status'], [user_reponse, opponent_response])
            print session['true_status']

            session['game_status']['faceup'] = lookup_cards([session['true_status']['faceup']])
    else:
        session['true_status'] = cg.update()
        game_status = deepcopy(session['true_status'])
        game_status['hands'][1] = ["BB"] * len(game_status['hands'][1])
        game_status['hands'] = [lookup_cards(hand) for hand in game_status['hands']]
        session['game_status'] = game_status
    form = ResponseForm()


    return render_template('index.html',  game_status=session['game_status'], true_status=session['true_status'], form=form)

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
