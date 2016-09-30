import itertools
from random import shuffle, randint

suits = ['C', 'S', 'H', 'D']
values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


class PlainDeck(object):
    """
    Initialize Base Deck Class with Basic Create, Shuffle, Deal, and Cut
    functions.  Inherited by CribDeck
    """

    def __init__(self, deck=None):
        """
        Create Deck and shuffle cards.  Cards will be in the format "2H, KS"
        """
        if deck is None:
            self.deck = [''.join(list(x))
                         for x in itertools.product(values, suits)]
            shuffle(self.deck)
        else:
            self.deck = deck

    def draw_card(self):
        """
        Modify current deck and return drawn card
        INPUT: none
        OUTPUT: card from the top of the deck
        """
        return self.deck.pop(0)

    def cut_card(self):
        """
        Modify current deck and return drawn card from random location
        for the spirit of it :)
        INPUT: none
        OUTPUT: card from random location in the deck
        """
        a = self.deck.pop(randint(0, len(self.deck) - 1))
        return a


class CribDeck(PlainDeck):
    """
    Inherit PlainDeck functions, add cribbage specific functionality
    """

    def __init__(self, num_p=2, deck=None):
        """
        Deal out cards based on number of players (functionality as of now
        will be only tested for 2)
        """
        PlainDeck.__init__(self, deck)
        self.kitty = []
        self.num_p = num_p

    def deal(self, n_cards=6):
        """
        Deal out n_cards (default for 2p game is 6)
        Input: n_cards
        Output: nested list of hands for n_players
        """
        return [[self.draw_card() for i in range(n_cards)]
                for _ in range(self.num_p)]
