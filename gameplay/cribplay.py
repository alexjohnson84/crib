from deck import CribDeck

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
        if status == None:
            updated_status = self.deal_hands()
        elif status['phase'] == 'Score':
            updated_status = self.deal_hands(status)
        elif status['phase'] == 'Deal':
            updated_status = self.discard(status, response)
        elif status['phase'] == 'Discard':
            updated_status = self.turn(status)
        return updated_status

    def create_response(self, phase, scores, hands, deck, faceup=None):
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
        response_dict['faceup'] = faceup
        response_dict['deck'] = deck
        return response_dict

    def deal_hands(self, status=None):
        """
        Deal the hands, will have None status on first round of the game,
        After first round, status will contain a score

        Input: status from previous hand (if applicable)
        Output: Shuffled deck and new hand
        """
        phase = 'Deal'
        self.crib_deck = CribDeck(num_p=self.num_p)
        hands = self.crib_deck.deal()
        if status is not None:
            scores = status['scores']
        else:
            scores = [0,0]
        return self.create_response(phase,
                                    scores,
                                    hands,
                                    self.crib_deck.deck
                                    )

    def discard(self, status, response):
        phase = 'Discard'
        hands = status['hands']
        for hand, discards in zip(hands, response):
            for card in discards:
                hand.remove(card)
        return self.create_response(phase,
                                    status['scores'],
                                    hands,
                                    status['deck'])
    def turn(self, status):
        phase = 'Turn'
        c_deck = CribDeck(deck=status['deck'])
        faceup = c_deck.cut_card()
        return self.create_response(phase,
                                    status['scores'],
                                    status['hands'],
                                    c_deck.deck,
                                    faceup)
