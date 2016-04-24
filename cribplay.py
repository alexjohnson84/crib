from decktools import Decktools, prompt_action
from cribmodels import *
from random import shuffle
from cribtools import scorehand, peg
import pprint
import json
import os

def clear_terminal():
	os.system('cls' if os.name == 'nt' else 'clear')

def discard_two(hand, kitty, player, man = False):
	if man == True:
		selection = prompt_action(hand,"select cards to discard: ",2, str(player))
		kitty.append(selection)
		hand = list(set(hand)^set(selection))
	else:
		for i in range(2):
			kitty.append(hand[i])
		hand = hand[2:]
	return (hand, kitty)

def switch_player(current_player):
	if(current_player) == "p1":
		return "p2"
	else:
		return "p1"

class TwoPlayerGame():

	game_log = {}
	round_number = 1
	p1_score = 0
	p2_score = 0
	current_dealer = "p1" 

	def see_scores(self):
		return "p1 : " + str(self.p1_score) + ", p2 : " + str(self.p2_score)
		
	def playgame(self, man1, man2):
		game_num_str = "round " + str(self.round_number)
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

		if man1 == True or man2 == True:
			print("current dealer is " + str(self.current_dealer))
		(p1_hand, kitty) = discard_two(p1_hand,kitty, "Player 1", man1)
		(p2_hand, kitty) = discard_two(p2_hand,kitty, "Player 2", man2)
		#log initial discard
		self.game_log[game_num_str]["initial discard"] = {"p1_hand" : p1_hand, "p2_hand" : p2_hand,"kitty" : kitty}

		#cut & flip card
		face_up = current_deck.cut_card()
		if man1 == True or man2 == True:
			print("face up card is " + str(face_up))
			input("Press Enter to continue...")
			clear_terminal()

		#add nobs
		if 'J' in face_up[0]:
			if self.current_dealer == "p1":
				self.p2_score += 1
			else:
				self.p1_score += 1
			if man1 == True or man2 == True:
				print(str(self.current_dealer) + " got nobs!")
				input("Press Enter to continue...")

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
		
		while (len(p1_hand_peg) > 0 or len(p2_hand_peg) > 0):

			if current_pegger == "p1":
				if(len(p1_hand_peg)) > 0:
					p1_hand_peg = pegmodel_p1(p1_hand_peg)
					peg_round = peg("Player 1", p1_hand_peg, p2_hand_peg, current_count,peg_hist, man1, self.see_scores())
					self.p1_score += peg_round[0]
					self.p2_score += peg_round[1]
					p1_hand_peg = peg_round[2]
					current_card = peg_round[3].split()
					peg_hist = peg_round[5]
					current_count = peg_round[4]
			if current_pegger == "p2":

				if(len(p2_hand_peg)) > 0:
					p2_hand_peg = pegmodel_p2(p2_hand_peg)
					peg_round = peg("Player 2", p2_hand_peg, p1_hand_peg, current_count,peg_hist, man2, self.see_scores())
					self.p2_score += peg_round[0]
					self.p1_score += peg_round[1]
					p2_hand_peg = peg_round[2]
					current_card = peg_round[3].split()
					peg_hist = peg_round[5]
					current_count = peg_round[4]
			clear_terminal()
					

			current_hist = peg_hist
			self.game_log[game_num_str]["pegging"][peg_action] = {"current_card": current_card, "current_pegger" : current_pegger, "p1_hand_peg" : p1_hand_peg, "p2_hand_peg" : p2_hand_peg, "current_count" : current_count, "peg_hist": current_hist, "p1_score" : self.p1_score, "p2_score" : self.p2_score}
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
		self.game_log[game_num_str]["handscoring"] = {"p1 hand score" : scorehand(p1_hand,face_up), "p2 hand score" : scorehand(p2_hand,face_up), "kitty score" : scorehand(kitty, face_up)}
		self.game_log[game_num_str]["round_score"] = {"p1 round score" : self.p1_score, "p2 round score" : self.p2_score}


		#switch dealer
		self.current_dealer = switch_player(self.current_dealer)

		self.round_number += 1
		#placeholder for testing
		#self.p1_score = 120

	def __init__(self, man1 = False, man2 = False):
		while (self.p1_score < 120 and self.p2_score < 120):
			self.playgame(man1, man2)
		#scoring doesn't go above 120
		if self.p1_score > 120:
			self.p1_score = 120
		if self.p2_score > 120:
			self.p2_score = 120
		#log final scores
		self.game_log["final score"] = {"p1 final score" : self.p1_score, "p2 final score" : self.p2_score}
		#pprint.pprint(self.game_log)
		with open('data.txt', 'w') as outfile:
			json.dump(self.game_log, outfile, indent = 4, sort_keys = True)

a = TwoPlayerGame(True, True)
#print(a.game_log['game 1']['pegging'])




