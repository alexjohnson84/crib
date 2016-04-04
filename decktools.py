import itertools
from random import shuffle

suits = ['C', 'S', 'H', 'D']
values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

def deck_init():
	deck = [list(x) for x in itertools.product(values,suits)]
	deck = [x[0] + x[1] for x in deck]
	shuffle(deck)
	return deck
	

#print(deck_init())
#print(len(deck_init()))
#print([list(x) for x in deck_init()])