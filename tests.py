import unittest
from decktools import Decktools
from cribtools import scorehand
import json

test_hands = json.load(open("test_files/test_hands.txt"))



#read a hand from specific example
def read_hand(hands,ptype,example):
	return(eval(hands[ptype][example]))
#list examples from test hand file
def list_examples(hands,ptype):
	examps = list([k for k in hands[ptype].keys() if k[0:1] == "ex"])
	return examps
def define_testcase(src, h_type,score, turn_up = False):
	for example in list_examples(src,h_type):
		if(turn_up == False):
			self.assertEqual(scorehand(read_hand(src, h_type, example)),score)
		if(turn_up == True):
			self.assertEqual(scorehand(read_hand(src, h_type, example)), scorehand(read_hand(src, h_type, "turn_" + example)),score)

class TestDeck(unittest.TestCase):
	#test to see deck has 52 cards
	def test_deck_length(self):
		t_deck = Decktools()
		self.assertEqual(len(t_deck.deck),52)
	#test drawing and cutting functions
	def test_draw(self):
		t_deck = Decktools()
		t_deck.draw_card()
		self.assertEqual(len(t_deck.deck),51)
		t_deck.cut_card()
		self.assertEqual(len(t_deck.deck),50)

class TestCrib(unittest.TestCase):
	def test_fifteen(self):
		define_testcase(test_hands, "fifteen",2)

	def test_pairs(self):
		define_testcase(test_hands, "pair",2)

	def test_straight(self):
		define_testcase(test_hands, "straight_3",3)
		define_testcase(test_hands, "straight_4",4)
		define_testcase(test_hands, "straight_5",5)

	def test_flush(self):
		define_testcase(test_hands, "flush_4",4)
		define_testcase(test_hands, "flush_5",5)

	def test_nobs(self):
		define_testcase(test_hands, "nobs", 1, True)

	def test_mixed_cases(self):
		define_testcase(test_hands, "8 point",8)
		define_testcase(test_hands, "10 point",10)
		define_testcase(test_hands, "15 point",15)
		define_testcase(test_hands, "16 point", 16)
		define_testcase(test_hands, "29 point", 29, True)
				

if __name__ == '__main__':
    unittest.main()