import unittest
from random import shuffle
from deck import CribDeck
from cribplay import CribGame
from cribbage_scoring import CribHandScore, CribPegScore

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
        self.assertEqual(new_status['kitty'], ['4S', 'QH', '10S', 'AS'])
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
    def test_pegging(self):
        cg = CribGame()
        old_status = self.test_status['test_pegging'][0]
        for i, play in enumerate(self.test_status['test_pegging']):
            if i == 0:
                pass
            else:
                response = play['test_response']
                new_status = cg.update(old_status, response)
                self.assertEqual(new_status['scores'], play['scores'])
                self.assertEqual(new_status['peg_hist'], play['peg_hist'])
                self.assertEqual(new_status['pegger'], play['pegger'])
                for i in range(len(new_status['hands'])):
                    self.assertEqual(set(new_status['hands'][i]),
                                     set(play['hands'][i])
                                     )
                    self.assertEqual(set(new_status['peg_phist'][i]),
                                     set(play['peg_phist'][i])
                                     )
                old_status = new_status

    def test_final_scoring(self):
        cg = CribGame()
        old_status = self.test_status['test_hand_scoring']
        test_scores = self.test_status['test_hand_scoring']['test_scores']
        new_status = cg.update(old_status)
        self.assertEqual(new_status['scores'], test_scores)


class TestHandScoring(unittest.TestCase):
    """
    Test scoring functions across different unique cases
    """
    with open('gameplay/test_files/test_hands.txt', 'r') as th:
        test_hands = eval(th.read())['handscore']
    cs = CribHandScore(score_type='hand')
    def test_hand_fifteen(self):
        for key, example in self.test_hands['fifteen'].iteritems():
            self.assertEqual(self.cs.score(eval(example)), 2)
    def test_hand_fifteen_turn(self):
        for key, example in self.test_hands['fifteen_turn'].iteritems():
            if key[:2] == 'ex':
                self.assertEqual(
                    self.cs.score(eval(example),
                                    eval(self.test_hands['fifteen_turn']
                                        ['turn_' + key])
                                        )
                                ,2)
    def test_pairs(self):
        for example in self.test_hands['pair'].values():
            self.assertEqual(self.cs.score(eval(example)), 2)
    def test_flushes(self):
        for example in self.test_hands['flush_4'].values():
            self.assertEqual(self.cs.score(eval(example)), 4)
        for example in self.test_hands['flush_5'].values():
            self.assertEqual(self.cs.score(eval(example)), 5)
    def test_longest_consecutive_seq(self):
        seq = [8,7,6,4,3,2,1]
        long_seq = self.cs._longest_consecutive_sequence(seq)
        self.assertEqual(long_seq, [1,2,3,4])
        seq = [8,7,6,5,3,2,1]
        shuffle(seq)
        long_seq = self.cs._longest_consecutive_sequence(seq)
        self.assertEqual(long_seq, [5,6,7,8])

    def test_straights(self):
        length_scores = [(2,0), (3,3), (4,4), (5,5)]
        for length, score in length_scores:
            for example in self.test_hands['straight_' + str(length)].values():
                self.assertEqual(self.cs.score(eval(example)), score)
    def test_nobs(self):
        for key, example in self.test_hands['nobs'].iteritems():
            if key[:2] == 'ex':
                turn = eval(self.test_hands['nobs']['turn_' + key])
                score = self.cs.score(eval(example), turn)
                self.assertEqual(score, 1)
    def test_edge_cases(self):
        cases = [8,10,15,16]
        for case_score in cases:
            case_key = '%s point' % (case_score)
            for key, example in self.test_hands[case_key].iteritems():
                self.assertEqual(self.cs.score(eval(example)),
                                case_score,
                                '%s failed, %s != %s' % (example,
                                                    case_score,
                                                    self.cs.score(eval(example))
                                                    )
                                )
    def test_perfect_hand(self):
        for key, example in self.test_hands['29 point'].iteritems():
            if key[:2] == 'ex':
                turn = eval(self.test_hands['29 point']['turn_' + key])
                score = self.cs.score(eval(example), turn)
                self.assertEqual(score, 29)

class TestPegScoring(unittest.TestCase):
    with open('gameplay/test_files/test_hands.txt', 'r') as th:
        test_hands = eval(th.read())['pegscore']
    def test_peg_scoring(self):
        for ex_type, test_set in self.test_hands.iteritems():
            for example in test_set.values():
                cps = CribPegScore(eval(example['hist']))
                self.assertEqual(cps.score,
                                example['score'],
                                "%s != %s, example: %s for hist %s" % (cps.score,
                                                            example['score'],
                                                            ex_type,
                                                            example['hist']))
                if 'count' in example:
                    self.assertEqual(cps.count,
                                    example['count'],
                                    "%s != %s, example: %s for hist %s" % (cps.count,
                                                                example['count'],
                                                                ex_type,
                                                                example['hist']))




if __name__ == '__main__':
    unittest.main()
