from decktools import Decktools
from cribmodels import *
from random import shuffle
from cribtools import scorehand, peg
import pprint

def discard_two(hand, kit):
	kitty = kit
	for i in range(2):
		kitty.append(hand[i])
	handy = hand[2:]
	return (handy, kitty)

def switch_player(current_player):
	if(current_player) == "p1":
		return "p2"
	else:
		return "p1"

class TwoPlayerGame():

	game_log = {}
	game_number = 1
	p1_score = 0
	p2_score = 0
	current_dealer = "p1" 

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
		current_count = 0
		peg_action = 0
		#non dealer goes first
		current_pegger = switch_player(self.current_dealer)
		p1_hand_peg, p2_hand_peg = p1_hand, p2_hand
		peg_hist, current_hist, current_card = [], [],[]
		#log initial state
		self.game_log[game_num_str]["pegging"] = {peg_action : {"current_pegger" : "NA", "p1_hand_peg" : p1_hand_peg, "p2_hand_peg" : p2_hand_peg, "current_count" : current_count, "peg_hist" : current_hist}}
		peg_action += 1
		#print(self.game_log['game 1']['pegging'])
		#TODO finish this section
		
		while (len(p1_hand_peg) > 0 or len(p2_hand_peg) > 0):
			"""
			if current_pegger == "p1":
				if(len(p1_hand_peg)) > 0:
					p1_hand_peg = pegmodel_p1(p1_hand_peg, current_count)
					peg_round = peg(p1_hand_peg, current_count)
					#todo - create peg round function
					self.p1_score += peg_round[0]
					p1_hand_peg = peg_round[1]
					peg_hist.append(peg_round[2])
					current_count += peg_round[3]
				else:
					self.p2_score += 1
			if current_pegger == "p2":
				if(len(p2_hand_peg)) > 0:
					p2_hand_peg = pegmodel_p2(p2_hand_peg, current_count)
					peg_round = peg(p2_hand_peg, current_count)
					self.p2_score += peg_round[0]
					p2_hand_peg = peg_round[1]
					peg_hist.append(peg_round[2])
					current_count += peg_round[3]
			"""
			if current_pegger == "p1":
				if(len(p1_hand_peg)) > 0:
					p1_hand_peg = pegmodel_p1(p1_hand_peg)
					peg_round = peg(p1_hand_peg, p2_hand_peg, current_count)
					self.p1_score += peg_round[0]
					p1_hand_peg = peg_round[1]
					current_card = peg_round[2].split()
					peg_hist = peg_hist + current_card
					current_count = peg_round[3]
			if current_pegger == "p2":

				if(len(p2_hand_peg)) > 0:
					p2_hand_peg = pegmodel_p2(p2_hand_peg)
					#print(p1_hand,p2_hand)
					#print(peg(p2_hand_peg, p1_hand_peg, current_count))
					peg_round = peg(p2_hand_peg, p1_hand_peg, current_count)
					self.p2_score += peg_round[0]
					p2_hand_peg = peg_round[1]
					current_card = peg_round[2].split()
					peg_hist = peg_hist + current_card
					current_count = peg_round[3]
					

			current_hist = peg_hist
			self.game_log[game_num_str]["pegging"][peg_action] = {"current_card": current_card, "current_pegger" : current_pegger, "p1_hand_peg" : p1_hand_peg, "p2_hand_peg" : p2_hand_peg, "current_count" : current_count, "peg_hist": current_hist}
			peg_action += 1
			current_pegger = switch_player(current_pegger)

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
		self.current_dealer = switch_player(self.current_dealer)
		#placeholder for testing
		self.p1_score = 120

	def __init__(self):
		while (self.p1_score < 120 and self.p2_score < 120):
			self.playgame()
		#pprint.pprint(self.game_log)

#a = TwoPlayerGame()
#print(a.game_log['game 1']['pegging'])




