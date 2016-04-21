import unittest
from cribplay import TwoPlayerGame
from decktools import Decktools
from cribtools import scorehand
import json

test_hands = json.load(open("test_files/test_hands.txt"))



#read a hand from specific example
def read_hand(hands,scoretype, h_type,example):
	return(eval(hands[scoretype][h_type][example]))
#list examples from test hand file
def list_examples(hands,scoretype,ptype):
	examps = list([k for k in hands[scoretype][ptype].keys() if k[0:2] == "ex"])
	return examps

def define_testcase(src, scoretype, h_type,score, turn_up = False, is_equal = True):
	if(scoretype == "handscore"):
		for example in list_examples(src, scoretype, h_type):
			if(turn_up == False):
				assert scorehand(read_hand(src, scoretype, h_type, example)) == score
			if(turn_up == True):
				assert scorehand(read_hand(src, scoretype, h_type, example),read_hand(src, scoretype, h_type, "turn_" + example)) == score
	if(scoretype == "pegscore"):
		for example in list_examples(src, scoretype, h_type):
			if(is_equal == True):
				self.assertEqual(scorehand(read_hand(src, h_type, example)),score)
			if(is_equal == False):
				self.assertNotEqual(scorehand(read_hand(src, h_type, example)),score)

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
		define_testcase(test_hands, "handscore", "fifteen",2)

	def test_pairs(self):
		define_testcase(test_hands, "handscore", "pair",2)

	def test_straight(self):
		define_testcase(test_hands, "handscore", "straight_3",3)
		define_testcase(test_hands, "handscore", "straight_4",4)
		define_testcase(test_hands, "handscore", "straight_5",5)

	def test_flush(self):
		define_testcase(test_hands, "handscore", "flush_4",4)
		define_testcase(test_hands, "handscore", "flush_5",5)


	def test_nobs(self):
		define_testcase(test_hands, "handscore", "nobs", 1, True)

	def test_mixed_cases(self):
		define_testcase(test_hands, "handscore", "8 point",8)
		define_testcase(test_hands, "handscore", "10 point",10)
		define_testcase(test_hands, "handscore", "15 point",15)
		define_testcase(test_hands, "handscore", "16 point", 16)

		define_testcase(test_hands, "handscore", "29 point", 29, True)
"""
class TestPeg(unittest.TestCase):
	#todo - test pegging
	
	def test_pair_patterns(self):
		#define_testcase(test_hands, "pegscore", "doubles",2)
		#define_testcase(test_hands, "pegscore", "not_doubles", 2, False, True)
		#define_testcase(test_hands, "pegscore", "triples",3)
		#define_testcase(test_hands, "pegscore", "not_triples", 3, False, True)
		pass
	def test_straight_patterns(self):
		#define_testcase(test_hands, "pegscore", "straight_7",7)
		pass
	"""	
		
class TestPlay(unittest.TestCase):
	t_log = {}
	@classmethod
	def setUpClass(cls):
		t_play = TwoPlayerGame()
		cls.t_log = t_play.game_log
	#hand is shuffled, each player recieves 6 cards
	def test_initial_deal(self):
		self.assertEqual(len(self.t_log["game 1"]["initial deal"]["p1_hand"]),6)
		self.assertEqual(len(self.t_log["game 1"]["initial deal"]["p2_hand"]),6)
	#each player discards 2 cards based on model, this gets moved into "kitty"
	def test_initial_discard(self):
		self.assertEqual(len(self.t_log["game 1"]["initial discard"]["p1_hand"]),4)
		self.assertEqual(len(self.t_log["game 1"]["initial discard"]["p2_hand"]),4)
		self.assertEqual(len(self.t_log["game 1"]["initial discard"]["kitty"]),4)
	#they cut a card - upturn value is stored
	def test_card_flip(self):
		self.assertEqual(len(self.t_log["game 1"]["turn"]["face_up"]),1)
		self.assertEqual(self.t_log["game 1"]["turn"]["deck_length"],39)
	#players begin pegging - Test cases invoked in testpeg class
	def test_pegging(self):
		#test history is logging appropriately
		for key in self.t_log["game 1"]["pegging"].keys():
			self.assertEqual(len(self.t_log["game 1"]["pegging"][key]["peg_hist"]), key, "peg action #" + str(key) + " failed")
		#test that peg action #1 is opponent, peg action #3 is dealer
		#test that "go" is returned by opponent who can't play
		#test that "last card" registers a point


	#after all cards are on the table, scoring round moves on, first scoring is done by non-dealer then dealer
	#data from round is then logged and stored

				

if __name__ == '__main__':
    unittest.main()