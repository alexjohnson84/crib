import unittest
from deck import CribDeck
from cribplay import CribGame

class TestDeck(unittest.TestCase):
    """
    Check Deck functionality, ensure utilities are functional
    """
    def test_deck_length(self):
        """
        Check length of deck and check to make sure there are no duplicates
        """
        cd = CribDeck()
        self.assertEqual(len(cd.deck), 52)
        self.assertEqual(len(set(cd.deck)), 52)
    def test_draw_actions(self):
        """
        Check cut and draw actions, validate deck length and datatype of
        removed cards
        """
        cd = CribDeck()
        dc = cd.draw_card()
        self.assertEqual(len(cd.deck), 51)
        self.assertTrue(type(dc) is str)
        # Cut Cards
        cc = cd.cut_card()
        self.assertEqual(len(cd.deck), 50)
        self.assertTrue(type(cc) is str)
    def test_deal(self):
        """
        Check dealing functionality for 2 player game.  May need to change if
        number of players is updated
        """
        cd = CribDeck()
        hands = cd.deal()
        self.assertEqual(len(hands), 2)
        self.assertEqual(len(hands[0]), 6)
        self.assertEqual(len(hands[1]), 6)
        self.assertTrue(type(hands[0][0]) is str)

class TestGamePlay(unittest.TestCase):
    with open('gameplay/test_files/test_status.txt', 'r') as tf:
        test_status = eval(tf.read())

    def test_new_game_deal(self):
        """
        Test a new deal of the game with no prior actions within the game

        test: phase change, scores exist and are 0, and length of deck is
        correct
        """
        cg = CribGame()
        status = cg.update()
        self.assertEqual(status['phase'], 'Deal')
        self.assertEqual(status['scores'], [0,0])
        self.assertEqual(len(status['deck']), 40)
    def test_continued_game_deal(self):
        """
        Test Flow for starting a new round in continued game
        """
        old_status = self.test_status['test_continued_game_deal']
        cg = CribGame()
        new_status = cg.update(old_status)
        self.assertEqual(old_status['scores'], new_status['scores'])
        self.assertNotEqual(old_status['deck'], new_status['deck'])
        self.assertEqual(new_status['phase'], 'Deal')
        self.assertEqual(new_status['faceup'], None)
        self.assertEqual(len(new_status['deck']), 40)

    def test_discard(self):
        """
        Test discarding, ensure status is updated, cards from post request are
        discarded.
        """
        old_status = self.test_status['test_discard']
        cg = CribGame()
        response = [['4S', 'QH'], ['10S', 'AS']]
        new_status = cg.update(old_status, response)

        self.assertEqual(new_status['phase'], 'Discard')

        self.assertEqual(len(set(new_status['hands'][0])\
                            .intersection(response[0])), 0)
        self.assertEqual(len(set(new_status['hands'][1])\
                            .intersection(response[1])), 0)
    def test_turn(self):
        """
        Test that the card is turned and that the deck is updated from
        cut card
        """
        old_status = self.test_status['test_turn']
        cg = CribGame()
        new_status = cg.update(old_status)

        self.assertTrue(type(new_status['faceup']) is str)
        self.assertEqual(len(new_status['deck']), 39)


if __name__ == '__main__':
    unittest.main()
