import itertools
from random import shuffle, randint

suits = ['C', 'S', 'H', 'D']
values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

class Decktools:

	def __init__(self):
		deck_init = [list(x) for x in itertools.product(values,suits)]
		deck = [x[0] + x[1] for x in deck_init]
		shuffle(deck)
		self.deck = deck
		


	def draw_card(self):
		return self.deck.pop(0)
	#cut the card for the spirit of it :)
	def cut_card(self):
		return self.deck.pop(randint(0,len(self.deck)))
			
	#return deck

#a = Decktools()
#print(a.deck)
#print(len(deck_init()))
#print([list(x) for x in deck_init()])