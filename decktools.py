import itertools
from random import shuffle, randint
import pprint

suits = ['C', 'S', 'H', 'D']
values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

#read a hand from specific example
def read_hand(hands,scoretype, h_type,example):
	return(eval(hands[scoretype][h_type][example]))

def prompt_action(cards,prompt, num_play, player):
	valid_input = False
	while valid_input == False:
		print(str(player) + " Action!")
		print("Cards : " + str(cards))
		choice = str(input(prompt))
		choice = choice.split(',')
		try:
			choice = list(map(int,choice))
			if len(choice) != num_play:
				print("incorrect number of cards selected")
			elif(min(choice) > 0 and max(choice) <= len(cards)):
				valid_input = True
			else:
				print("value out of range, try again") 
		except:
			print("input error, try again!")
	return [cards[a-1] for a in choice]



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
		a = self.deck.pop(randint(0,len(self.deck)-1))
		return a.split()
			
	#return deck

#a = Decktools()
#print(a.deck)
#print(len(deck_init()))
#print([list(x) for x in deck_init()])
#print(prompt_action(['10D', 'JH', 'QS','KH','QD'],"select cards to discard: ",2))