from decktools import Decktools
from cribmodels import *
from random import shuffle
from cribtools import scorehand

def discard_two(hand, kit):
	kitty = kit
	for i in range(2):
		kitty.append(hand[i])
	handy = hand[2:]
	return (handy, kitty)


class TwoPlayerGame():

	game_log = {}
	game_number = 1
	p1_score = 0
	p2_score = 0
	current_dealer = "p1" 
	"""
	def pegging(self,p1_hand,p2_hand):
		current_count = 0
		pegmodel(p1_hand)
	"""


	def playgame(self):
		game_num_str = "game " + str(self.game_number)
		self.game_log[game_num_str] = {}
		current_deck = Decktools()
		p1_hand = []
		p2_hand = []
		kitty = []
		#each player gets 6 cards
		for i in range(0,6):
			p1_hand.append(str(current_deck.draw_card()))
			p2_hand.append(current_deck.draw_card())
		#log Initial deal
		self.game_log[game_num_str]["initial deal"] = {"p1_hand" : p1_hand, "p2_hand" : p2_hand, "current_dealer" : self.current_dealer}
		#apply model for discard
		cribmodel_p1(p1_hand)
		cribmodel_p2(p2_hand)

		(p1_hand, kitty) = discard_two(p1_hand,kitty)
		(p2_hand, kitty) = discard_two(p2_hand,kitty)
		#log initial discard
		self.game_log[game_num_str]["initial discard"] = {"p1_hand" : p1_hand, "p2_hand" : p2_hand,"kitty" : kitty}

		#cut & flip card
		face_up = current_deck.cut_card()

		#add nobs
		if 'J' in face_up[0]:
			if self.current_dealer == "p1":
				self.p2_score += 1
			else:
				self.p1_score += 1

		self.game_log[game_num_str]["turn"] = {"face_up" : face_up, "deck_length" : len(current_deck.deck)}
		#TODO - do pegging here

		#score cards
		if self.current_dealer == "p1":
			self.p2_score += scorehand(p2_hand,face_up)
			self.p1_score += scorehand(p1_hand,face_up)
			self.p1_score += scorehand(kitty, face_up)
		else:
			self.p1_score += scorehand(p1_hand,face_up)
			self.p2_score += scorehand(p2_hand,face_up)
			self.p2_score += scorehand(kitty, face_up)

		#switch dealer
		if self.current_dealer == "p1":
			self.current_dealer = "p2"
		else:
			self.current_dealer = "p1"
		#placeholder for testing
		self.p1_score = 120

	def __init__(self):
		while (self.p1_score < 120 and self.p2_score < 120):
			self.playgame()
		#print(self.game_log)

#a = TwoPlayerGame()
#print(a.game_log)




