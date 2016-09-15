from deck import CribDeck
from cribbage_scoring import CribHandScore, CribPegScore

class CribGame(object):
    """
    Main Class for Cribbage Gameplay.  Utilizes a status dict to allow
    communication between frontend and class to facilitate independent requests

    Example API for frontend.  Dict stored as a session variable
    {phase:"pegging",
    scores: [45, 67],
    hands: [['5C', '10S', '8H', '6S', '3D', 'KC'],
             ['KS', 'JD', '6D', '6H', '9C', '7S']],
    faceup: '4H',
    deck: [list of remaining cards]}
    """
    def __init__(self, num_p=2):
        """
        Initialize object and set num players (currently only tested with two)
        """
        self.num_p = num_p
    def update(self, status=None, response=None):
        """
        read in status and response variables, and actions upon them.
        Returns the status response variable to be actioned upon by the
        frontend
        """
        self.current_phase = 'Nun'
        if status is not None:
            self.current_phase = status['phase']
        if status == None:
            updated_status = self.deal_hands()
        elif self.current_phase == 'Score':
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

    def create_response(self, phase, scores, hands, deck, faceup=None,
                            peg_phist={0:[], 1:[]}, peg_hist=[], kitty=[], dealer=0,
                            pegger=None):
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
        return response_dict

    def switch_player(self, cur_player):
        """
        Switch player
        Input: int {0,1}
        Output: int {0,1} switched from current player
        """
        return abs(cur_player-1)

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
            scores = [0,0]
            dealer = 0
        return self.create_response(phase,
                                    scores,
                                    hands,
                                    self.crib_deck.deck,
                                    dealer = dealer
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

        #extra 2 points for flipping a jack
        if faceup[0] == 'J':
            scores[status['dealer']] += 2

        return self.create_response(phase,
                                    status['scores'],
                                    status['hands'],
                                    c_deck.deck,
                                    faceup,
                                    kitty=status['kitty'],
                                    dealer=status['dealer'])

    def pegging(self, status, response):
        """
        For each user, ingest status,response, and update score/status per
        action
        """
        phase = 'Pegging'
        if status['pegger'] == None:
            player = self.switch_player(status['dealer'])
        else:
            player = self.switch_player(status['pegger'])
        player_pegs = len(status['peg_phist'][player])
        scores = status['scores']
        while player_pegs < 4:
            hand = status['hands'][player]
            selection = hand.pop(hand.index(response))
            #append as list in case of null list
            status['peg_hist'] += [selection]
            status['peg_phist'][player] += [selection]

            cps = CribPegScore(status['peg_hist'])
            scores[player] += cps.score
            return self.create_response(phase,
                                        scores,
                                        status['hands'],
                                        status['deck'],
                                        status['faceup'],
                                        kitty=status['kitty'],
                                        dealer=status['dealer'],
                                        peg_hist=status['peg_hist'],
                                        peg_phist=status['peg_phist'],
                                        pegger=player
                                        )
        phase = 'Pegging Complete'
        hands = [status['peg_phist'][key] for key in [0,1]]
        return self.create_response(phase,
                                    scores,
                                    hands,
                                    status['deck'],
                                    status['faceup'],
                                    kitty=status['kitty'],
                                    dealer=status['dealer'],
                                    pegger=None
                                    )
    def hand_scoring(self, status):
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
                                    dealer=status['dealer'],
                                    )
