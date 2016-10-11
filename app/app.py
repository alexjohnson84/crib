import numpy as np
from flask import Flask, session, render_template, url_for, request, redirect
from gameplay.cribplay import CribGame, find_legal_moves, find_best_hand_combination, find_best_peg
from gameplay.cribbage_scoring import CribPegScore
from copy import deepcopy
from forms import ResponseForm

import random
import datetime
from pprint import pprint
import logging
import uuid
logging.basicConfig(filename='app/example.log', level=logging.INFO, format='%(asctime)s %(message)s')

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
                'selection': 0},
                'Game Over': {'cue': 'End Of Game',
                'selection': 0}
                }

app = Flask(__name__, static_url_path='/app/static')
app.config.from_object('config')
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.String(50))
    games_won = db.Column(db.Integer, default=0)
    games_lost = db.Column(db.Integer, default=0)
    def __init__(self, u_id):
        self.u_id = u_id
    def add_game(self, iswin):
        if iswin == True:
            self.games_won += 1
        else:
            self.games_lost += 1

with open('app/static/mapping/card_dir.txt') as f:
    img_map = eval(f.read())

def lookup_cards(lst):
    card_paths = []
    for card in lst:
        card_paths.append([card, url_for('static', filename=img_map[card])])
    return card_paths


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
        ul = UserLogs(str(session['history']))
        db.session.add(ul)
        db.session.commit()

def get_best_peg_response(status, active_player, return_all=False):
        legal_moves = find_legal_moves(status['peg_count'],
                                            status['hands'][active_player]
                                            )
        if len(legal_moves) == 0:
            response = ['GO']
        else:
            if status['phase'] != 'Game Over':
                response = find_best_peg(legal_moves, status, return_all)
            else:
                response = None
        return response


cg = CribGame()


@app.route('/index', methods=['GET', 'POST'])
def index():
    try:
        session['instructions'] = deepcopy(instructions)
        if 'user_id' not in session:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
            usr = Users(user_id)
            db.session.add(usr)
            db.session.commit()
        else:
            user_id = session['user_id']


        session['legal_moves'] = 'null'
        session['move_scores'] = None
        if request.method == 'POST':
            session['discard_selection'] = request.values['discard_selection']
            return redirect(url_for('index'))
        obscure_hand = True
        save = False
        if 'true_status' not in session:
            session['true_status'] = cg.update()
            session['move_scores'] = find_best_hand_combination(session['true_status']['hands'][0], session['true_status']['dealer'], return_all=True)
        elif session['true_status']['phase'] == 'Deal':
            if 'discard_selection' in session:
                user_response = session['discard_selection'].split(',')
                opponent_response = find_best_hand_combination(session['true_status']['hands'][1], session['true_status']['dealer'])
                session['true_status'] = cg.update(session['true_status'], [user_response, opponent_response])
        elif session['true_status']['phase'] == 'Discard':
            session['true_status'] = cg.update(session['true_status'])
            if session['true_status']['dealer'] == 0:
                session['instructions']['Turn']['selection'] = 0
            else:
                session['instructions']['Turn']['selection'] = 1
                session['move_scores'] = get_best_peg_response(session['true_status'], 0, return_all=True)
            print "turn selection ", session['instructions']['Turn']['selection']

        elif session['true_status']['phase'] in ['Pegging', 'Turn']:
            if session['true_status']['pegger'] == 0:
                user_response = session['discard_selection']
                session['true_status'] = cg.update(session['true_status'], user_response)
            if session['true_status']['phase'] != 'Pegging Complete':
                opponent_response = get_best_peg_response(session['true_status'], 1)
                session['true_status'] = cg.update(session['true_status'], opponent_response)
                session['move_scores'] = get_best_peg_response(session['true_status'], 0, return_all=True)
            #user go
            session['legal_moves'] = find_legal_moves(session['true_status']['peg_count'],
                                            session['true_status']['hands'][0]
                                            )
            # run go automatically
            while session['legal_moves'] == []:
                if session['true_status']['phase'] != 'Pegging Complete':
                    session['true_status'] = cg.update(session['true_status'], ['GO'])
                    opponent_response = get_best_peg_response(session['true_status'], 1)
                    session['true_status'] = cg.update(session['true_status'], opponent_response)
                session['legal_moves'] = find_legal_moves(session['true_status']['peg_count'],
                                                            session['true_status']['hands'][0]
                                                            )

            if session['true_status']['phase'] == 'Pegging Complete':
                session['legal_moves'] = 'null'

        elif session['true_status']['phase'] == 'Pegging Complete':
            session['legal_moves'] = 'null'
            session['true_status'] = cg.update(session['true_status'])
            obscure_hand = False
        elif session['true_status']['phase'] == 'Round Complete':
            session['legal_moves'] = 'null'
            session['true_status'] = cg.update(session['true_status'])
            session['move_scores'] = find_best_hand_combination(session['true_status']['hands'][0], session['true_status']['dealer'], return_all=True)
            obscure_hand = False
            save = True
        elif session['true_status']['phase'] == 'Game Over':
            print "game over logged into db"
            iswin = max(session['true_status']['scores']) == session['true_status']['scores'][0]
            usr = Users.query.filter_by(u_id=user_id).first()
            usr.add_game(iswin)
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for('reset'))


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
        game_status['peg_hist']= [lookup_cards([hand]) for hand in game_status['peg_hist']]
        game_status['peg_phist'] = {key:lookup_cards(val) for key,val in game_status['peg_phist'].iteritems()}
        session['game_status'] = game_status
        logging.info({'u_id':user_id, 'log':session['true_status']})

        return redirect(url_for('crib'))
    except:
        return redirect(url_for('reset'))


@app.route('/crib', methods=['GET'])
def crib():
    form = ResponseForm()
    discard_rounds = ['Deal', 'Turn', 'Pegging']
    if 'game_status' in session:
        if session['game_status']['phase'] in discard_rounds:
            c_class = 'discard'
        else:
            c_class = ''
        return render_template('index.html',  game_status=session['game_status'],
                                true_status=session['true_status'],
                                form=form,
                                cue=session['instructions'][session['game_status']['phase']],
                                card_class=c_class,
                                legal_moves=session['legal_moves'],
                                move_scores=session['move_scores'],
                                user_wl=session['user_wl'])
    else:
        return redirect(url_for('index'))

@app.route('/')
@app.route('/reset', methods=['GET'])
def reset():
    try:
        user_id = deepcopy(session['user_id'])
        session.clear()
        session['user_id'] = user_id
        active_user = Users.query.filter(Users.u_id == session['user_id']).first()
        session['user_wl'] = [active_user.games_won, active_user.games_lost]
    except:
        session['user_wl'] = [0,0]


    return redirect(url_for('index'))

@app.route('/blog')
def blog():
    if 'user_wl' in session:
        user_wl = session['user_wl']
    else:
        user_wl = [0,0]
    return render_template('blog.html', user_wl=session['user_wl'])

@app.errorhandler(500)
def server_error():
    return redirect(url_for('reset'))

if __name__ == '__main__':
    app.run(debug=True)
