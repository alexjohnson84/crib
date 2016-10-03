from deck import CribDeck
from cribbage_scoring import CribHandScore, CribPegScore
from itertools import combinations
from sklearn.externals import joblib
import numpy as np
from copy import deepcopy


"""
Load in hand and peg models as global variables
"""
hand_model = joblib.load('models/hand_model/model.pkl')
hand_model.set_params(mod__n_jobs=1)
peg_model = joblib.load('models/peg_model/model.pkl')
peg_model.set_params(mod__n_jobs=1)

def find_legal_moves(count, hand):
    """
    For pegging actions
    INPUT: count(int), hand(list)
    OUTPUT: List of legal moves.  If no legal moves are available return null
    list
    """
    if len(hand) == 0:
        return []
    with open('gameplay/reference_files/value_map.txt', 'r') as vm:
        value_map = eval(vm.read())
    card_points = \
        [value_map['numbers'][val[:-1]] for val in hand]
    remaining_pts = 31 - count
    legal_moves = [hand[i] for i, val in enumerate(card_points)
                   if val <= remaining_pts]
    return legal_moves

def find_best_hand_combination(hand, is_dealer, return_all=False):
    """
    Build all 4 card combinations from 6 initial cards (24 total)
    Run model across all 24 combos, select card combo with the highest predicted score
    determine which cards out of the best 4 were discarded, return discards

    INPUT: player hand(list), is_dealer(bool)
    OUTPUT: 2 cards to discard (list)
    """
    combos = [[str(list(combo)), is_dealer] for combo in combinations(hand, 4)]
    preds = hand_model.predict(combos)
    if return_all == False:
        best_pred_hand = eval(combos[np.argmax(preds)][0])
        discards = [card for card in hand if card not in best_pred_hand]
        return discards
    else:
        discards_and_preds = []
        for pred_score, combo in zip(preds, combos):
            score = pred_score
            discards = [card for card in hand if card not in eval(combo[0])]
            discards_and_preds.append([discards, score])
        return discards_and_preds


def extract_peg_features(status, move):
    """
    Extract peg features and put them in the form to be ingested by model
    INPUT: status(dict), move(str)
    OUTPUT: list in the form of : [hand, len(hist), hist, len_opponent, count]
    """
    player = status['pegger']
    hand = deepcopy(status['hands'][player]).remove(move)
    hist = status['peg_hist'] + [move]
    len_opponent = len(status['hands'][abs(player - 1)])
    cps = CribPegScore(hist)
    count = cps.count
    return [hand, len(hist), hist, len_opponent, count]

def find_best_peg(legal_moves, status, return_all=False):
    """
    Peg model across all legal moves, return the best move
    INPUT: legal_moves(list), status(dict)
    OUPUT: best card to play (str)
    """
    max_pred_points = 0
    best_move = legal_moves[0]
    if return_all == False:
        for move in legal_moves:
            feats = extract_peg_features(status, move)
            pred_points = peg_model.predict([feats])
            if pred_points > max_pred_points:
                max_pred_points = pred_points
                best_move = move
        return best_move
    else:
        all_moves = []
        for move in legal_moves:
            feats = extract_peg_features(status, move)
            all_moves.append([move, float(peg_model.predict([feats]))])
        return all_moves




class CribGame(object):
    """
    Main Class for Cribbage Gameplay.  Utilizes a status dict to allow
    communication between frontend and class to facilitate independent requests

    Example API for frontend.  Dict stored as a session variable in the
    following format

    {
        u 'peg_count': 0,
        u 'deck': [u '3H', u 'JD', u 'KD', u '4H', u '2D', u '4C', u 'JS', u 'JH', u '5D', u '2C', u '9S', u 'KS', u '6H', u '8H', u '10D', u '6S', u '10S', u 'AD', u '4D', u '7H', u '5H', u '5S', u '8D', u 'AC', u '8C', u '6C', u '4S', u 'AS', u '5C', u 'AH', u 'QD', u '7D', u '9C', u '2H', u '8S', u '10C', u '3C', u 'QS', u '9H', u '7S'],
        u 'kitty': [u '3S', u '3D', u '10H', u 'KC'],
        u 'faceup': None,
        u 'scores': [116, 96],
        u 'pegger': None,
        u 'phase': u 'Discard',
        u 'peg_hist': [],
        u 'hands': [
                [u '6D', u '9D', u 'KH', u 'JC'],
                [u '7C', u 'QC', u '2S', u 'QH']
        ],
        u 'peg_phist': {
                u '1': [],
                u '0': []
        },
        u 'dealer': 0
    }
    """

    def __init__(self, num_p=2):
        """
        Initialize object and set num players (currently only tested with two)
        """
        self.num_p = num_p
        self.current_phase = None

    def update(self, status=None, response=None):
        """
        read in status and response variables, and actions upon them.
        Returns the status response variable to be actioned upon by the
        frontend
        """
        if status is not None:
            scores = status['scores']
        else:
            scores = [0, 0]
        if max(scores) <= 120:
            if status is not None:
                self.current_phase = status['phase']
            if status is None:
                updated_status = self.deal_hands()
            elif self.current_phase == 'Round Complete':
                updated_status = self.deal_hands(status)
            elif self.current_phase == 'Deal':
                updated_status = self.discard(status, response)
            elif self.current_phase == 'Discard':
                updated_status = self.turn(status)
            elif self.current_phase == 'Turn' or status['phase'] == 'Pegging':
                updated_status = self.pegging(status, response)
            elif self.current_phase == 'Pegging Complete':
                updated_status = self.hand_scoring(status)
            return updated_status
        else:
            status['phase'] = 'Game Over'
            return status

    def create_response(
            self,
            phase,
            scores,
            hands,
            deck,
            faceup=None,
            peg_phist={
                '0': [],
                '1': []},
            peg_hist=[],
            kitty=[],
            dealer=0,
            pegger=None,
            peg_count=0):
        """
        Constructor for status response variables
        returns data in the following form:
        {phase:"pegging",
        scores: [45, 67],
        hands: [['5C', '10S', '8H', '6S', '3D', 'KC'],
                 ['KS', 'JD', '6D', '6H', '9C', '7S']],
        faceup: '4H',
        deck: [list of remaining cards]}
        """
        response_dict = dict()
        response_dict['phase'] = phase
        response_dict['scores'] = scores
        response_dict['hands'] = hands
        response_dict['deck'] = deck
        response_dict['faceup'] = faceup
        response_dict['peg_phist'] = peg_phist
        response_dict['peg_hist'] = peg_hist
        response_dict['kitty'] = kitty
        response_dict['dealer'] = dealer
        response_dict['pegger'] = pegger
        response_dict['peg_count'] = peg_count
        return response_dict

    def switch_player(self, cur_player):
        """
        Switch player
        Input: int {0,1}
        Output: int {0,1} switched from current player
        """
        return abs(cur_player - 1)

    def deal_hands(self, status=None):
        """
        Deal the hands, will have None status on first round of the game,
        After first round, status will contain a score

        Dealer also needs to be switched on consecutive rounds.  If this is the
        first round, the dealer defaults to player 0

        Input: status from previous hand (if applicable)
        Output: Shuffled deck and new hand
        """
        phase = 'Deal'
        self.crib_deck = CribDeck(num_p=self.num_p)
        hands = self.crib_deck.deal()
        if status is not None:
            scores = status['scores']
            dealer = self.switch_player(status['dealer'])
        else:
            scores = [0, 0]
            dealer = 0
        return self.create_response(phase,
                                    scores,
                                    hands,
                                    self.crib_deck.deck,
                                    dealer=dealer,
                                    peg_phist={'0': [], '1': []},
                                    peg_hist=[]
                                    )

    def discard(self, status, response):
        """
        Allow users to discard 2 cards from their hand, update
        status variables
        Input: game status, discards as [[a,b],[x,y]]
        """
        phase = 'Discard'
        hands = status['hands']
        kitty = []
        for hand, discards in zip(hands, response):
            for card in discards:
                hand.remove(card)
                kitty.append(card)
        return self.create_response(phase,
                                    status['scores'],
                                    hands,
                                    status['deck'],
                                    kitty=kitty,
                                    dealer=status['dealer'])

    def turn(self, status):
        """
        cut card for the turn, store in status variable
        """
        phase = 'Turn'
        c_deck = CribDeck(deck=status['deck'])
        faceup = c_deck.cut_card()
        scores = status['scores']

        # extra 2 points for flipping a jack
        if faceup[0] == 'J':
            scores[status['dealer']] += 2

        return self.create_response(phase,
                                    scores,
                                    status['hands'],
                                    c_deck.deck,
                                    faceup,
                                    kitty=status['kitty'],
                                    dealer=status['dealer'],
                                    peg_phist={'0': [], '1': []},
                                    peg_hist=[],
                                    pegger=self.switch_player(status['dealer'])
                                    )

    def pegging(self, status, response):
        """
        For each user, ingest status,response, and update score/status per
        action
        """
        phase = 'Pegging'
        pegger = status['pegger']
        player_pegs = len(status['peg_phist'][str(pegger)])
        min_pegs = min([len(hand) for player, hand in
                        status['peg_phist'].iteritems()])
        scores = status['scores']
        if min_pegs < 4:
            if response != ['GO']:
                # import pdb; pdb.set_trace()
                hand = status['hands'][pegger]
                selection = hand.pop(hand.index(response))
                status['peg_phist'][str(pegger)] += [selection]
                status['peg_hist'] += [selection]
            else:
                status['peg_hist'] += response

            cps = CribPegScore(status['peg_hist'])
            scores[pegger] += cps.score
            peg_count = cps.count
            pegger = self.switch_player(pegger)
            if min([len(hand) for player, hand in
                    status['peg_phist'].iteritems()]) != 4:
                return self.create_response(phase,
                                            scores,
                                            status['hands'],
                                            status['deck'],
                                            status['faceup'],
                                            kitty=status['kitty'],
                                            dealer=status['dealer'],
                                            peg_hist=status['peg_hist'],
                                            peg_phist=status['peg_phist'],
                                            pegger=pegger,
                                            peg_count=peg_count
                                            )
        phase = 'Pegging Complete'
        hands = [status['peg_phist'][key] for key in ['0', '1']]
        return self.create_response(phase,
                                    scores,
                                    hands,
                                    status['deck'],
                                    status['faceup'],
                                    kitty=status['kitty'],
                                    peg_hist=status['peg_hist'],
                                    peg_phist=status['peg_phist'],
                                    dealer=status['dealer'],
                                    pegger=pegger
                                    )

    def hand_scoring(self, status):
        """
        Run hand scoring model and finish out the round
        """
        phase = 'Round Complete'
        scores = status['scores']
        turn = status['faceup']
        chs = CribHandScore()
        for i in range(len(scores)):
            hand_score = chs.score(status['hands'][i], [turn])
            scores[i] += hand_score
            if i == status['dealer']:
                kitty_score = chs.score(status['kitty'], [turn])
                scores[i] += kitty_score
        return self.create_response(phase,
                                    scores,
                                    status['hands'],
                                    status['deck'],
                                    status['faceup'],
                                    kitty=status['kitty'],
                                    peg_phist={'0': [], '1': []},
                                    peg_hist=[],
                                    dealer=status['dealer'],
                                    )
