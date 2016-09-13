import unittest
from deck import CribDeck

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

if __name__ == '__main__':
    unittest.main()
