import unittest
from decktools import deck_init
from cribtools import scorehand
import json

test_hands = json.load(open("test_files/test_hands.txt"))

#read a hand from specific example
def read_hand(hands,ptype,example):
	return(eval(hands[ptype][example]))
#list examples from test hand file
def list_examples(hands,ptype):
	return(list(hands[ptype].keys()))

class TestDeck(unittest.TestCase):
	#test to see deck has 52 cards
	def test_deck(self):
		self.assertEqual(len(deck_init()),52)

class TestCrib(unittest.TestCase):
	#TODO - nuild an evaluate hand test on the "read hand function"
	def test_fifteen(self):
		#iterate through examples
		for example in list_examples(test_hands,"fifteen"):
			self.assertEqual(scorehand(read_hand(test_hands,"fifteen",example)),2)
	def test_pairs(self):
		#iterate through examples
		for example in list_examples(test_hands,"pair"):
			self.assertEqual(scorehand(read_hand(test_hands,"pair",example)),2)

if __name__ == '__main__':
    unittest.main()