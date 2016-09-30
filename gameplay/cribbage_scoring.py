import itertools
from collections import Counter
from copy import deepcopy
from functools import reduce


class CribHandScore(object):
    """
    Score cribbage hand
    """

    def __init__(self):
        """
        Initialize class
        """
        pass

    def score(self, hand, turn=None):
        """
        Score then hand, and if turn is present use it to build a full hand.
        INPUT: hand(list), turn(string, optional)
        OUTPUT: score (int)
        """
        self.hand = hand
        self.turn = turn
        if self.turn is not None:
            self.full_hand = hand + turn
        else:
            self.full_hand = hand
        with open('gameplay/reference_files/value_map.txt', 'r') as vm:
            self.value_map = eval(vm.read())
        self.value_counter, self.suit_counter = \
            self._value_and_suit_counters(self.full_hand)

        score = 0
        if self.score_type == 'hand':
            score += self._score_fifteens(self.full_hand)
            score += self._score_pairs(self.value_counter)
            score += self._score_flushes(self.suit_counter)
            score += self._score_runs(self.value_counter)
            score += self._score_nobs()

        return score

    def _value_and_suit_counters(self, hand):
        """
        Setup counter objects of values and suits
        """
        value_counter = Counter([card[:-1] for card in hand])
        suit_counter = Counter([card[-1] for card in hand])
        return value_counter, suit_counter

    def _score_fifteens(self, full_hand):
        """
        Check for all combos of cards from the full hand and add return number
        of 15's * 2 points
        """
        current_score = 0
        combos = []
        for i in range(2, len(full_hand) + 1):
            combos += list(itertools.combinations(full_hand, i))
        for cards in combos:
            combo_sum = 0
            for card in cards:
                combo_sum += int(self.value_map['numbers'][card[:-1]])
            if combo_sum == 15:
                current_score += 2
        return current_score

    def _score_pairs(self, value_counter):
        """
        Find duplicates of cards, and assign it a score based upon method
        varibale mapped_pair
        """
        mapped_pair = {2: 2, 3: 6, 4: 12}
        mapped_values = [mapped_pair[value] for value in value_counter.values()
                         if value >= 2]
        return sum(mapped_values)

    def _score_flushes(self, suit_counter):
        """
        Cribbage only gives points for 4 or 5 cards of same suit.  Checks
        for same suit and returns score
        """
        return sum([value for key, value in suit_counter.iteritems()
                    if value >= 4])

    def _score_runs(self, value_counter):
        """
        Map values to the item in sequence, sort, and find longest consecutive
        sequence
        """
        sequence_counter = {self.value_map['sequence'][key]: value
                            for key, value in value_counter.iteritems()}
        sort_seq_keys = sequence_counter.keys()
        longest_sequence = self._longest_consecutive_sequence(sort_seq_keys)

        if len(longest_sequence) >= 3:
            run_counter = [value for key, value in sequence_counter.iteritems()
                           if key in longest_sequence]
            mult_factor = reduce(lambda x, y: x * y, run_counter)
            return len(longest_sequence) * mult_factor
        else:
            return 0

    def _longest_consecutive_sequence(self, lst):
        """
        Helper function to find the longest consecutive sequence.
        INPUT: lst
        OUTPUT: values of longest straight
        """
        s_lst = sorted(lst)
        longest_list = [s_lst[0]]
        current_list = [s_lst[0]]
        for i in range(1, len(s_lst)):
            if s_lst[i - 1] + 1 == s_lst[i]:
                current_list.append(s_lst[i])
            else:
                current_list = [s_lst[i]]
            if len(current_list) > len(longest_list):
                longest_list = current_list
        return longest_list

    def _score_nobs(self):
        """
        Add extra point if jack is flipped
        """
        current_score = 0
        if self.turn is not None:
            flipped_suit = self.turn[0][-1]
            if "J" + flipped_suit in self.hand:
                current_score += 1
        return current_score


class CribPegScore(object):
    """
    Determine both the count and score of a cribbage hand
    """

    def __init__(self, history):
        """
        Ingest pegging history and return the score of the last card played, as
        well as the current count of the history
        INPUT: Pegging history
        OUTPUT: Pegging score, pegging count
        """
        with open('gameplay/reference_files/value_map.txt', 'r') as vm:
            self.value_map = eval(vm.read())
        self.history = deepcopy(history)

        self.r_hist = self.history[::-1]
        if 'GO' in self.history and self.history.count('GO') % 2 == 0:
            self.r_hist = self.r_hist[:self.r_hist.index('GO')]
        if self.history.count('GO') >= 3 and self.history.count('GO') % 2 == 1:
            go_idxs = [i for i, move in enumerate(self.r_hist) if move == 'GO']
            self.r_hist = self.r_hist[:go_idxs[1]]
        # check if 31 has been met
        idx_start = self._find_seq_start(self.r_hist)
        self.r_hist = self.r_hist[:idx_start]

        self.mapped_sequence = [self.value_map['sequence'][
            val[:-1]] for val in self.r_hist if val != 'GO']
        self.score = self._score_peg()
        self.count = self.check_count()
        # check for 15/31 counts
        if self.count == 15 or self.count == 31:
            self.score += 2
        if self.count == 31:
            self.r_hist = []
            self.count = 0
        # check for 'GO'
        if self.history[-1] == 'GO':
            self.score += 1
        # check for last card
        self.num_cards_played = \
            len([card for card in self.history if card != 'GO'])
        if self.num_cards_played == 8:
            self.score += 1

    def _score_peg(self):
        """
        Score last cards played and check if pairs or straights have been met
        """
        score = 0
        if len(self.r_hist) > 0:
            score += self._check_pair_points(self.r_hist)
            score += self._check_if_straight(self.r_hist)
        return score

    def _find_seq_start(self, lst):
        """
        Find the start of the history that are incorporated into the count and
        score, ex: if 31 or both users "GO" we don't count pairs or scores that
        go before the index of the start
        """
        card_points = []
        for val in lst:
            if val == 'GO':
                card_points.append(0)
            else:
                card_points.append(self.value_map['numbers'][val[:-1]])

        idx_start = len(card_points)
        for i, card in enumerate(card_points):
            total = sum(card_points[len(card_points) - i:])
            if total == 31 and i != len(card_points):
                idx_start = len(card_points) - i
        return idx_start

    def _check_pair_points(self, lst):
        """
        Check points for the pairs, needs to incorporate last card if
        it is to come up with valid points.
        """
        mapped_pair = {2: 2, 3: 6, 4: 12}
        last_card = lst[0][:-1]
        max_pair = 0
        for value in lst:
            if value[:-1] == last_card:
                max_pair += 1
            else:
                break
        if max_pair == 1:
            return 0
        else:
            return mapped_pair[max_pair]

    def _check_if_straight(self, lst):
        """
        Setup sliding window and find lengths of lists that are valid runs.
        return highest valid length of list
        """
        valid_runs = [True] * len(lst)
        for i in range(3, len(lst) + 1):
            sorted_seq = sorted(self.mapped_sequence[:i])
            for j in range(1, len(sorted_seq)):
                if sorted_seq[j] - sorted_seq[j - 1] != 1:
                    valid_runs[i - 1] = False
        # find last occurence
        neg_index = valid_runs[::-1].index(True)
        longest_run = len(lst) - neg_index
        if longest_run >= 3:
            return longest_run
        else:
            return 0

    def check_count(self):
        """
        Check the current count
        History is sliced on the last 2 'GOs' and reduced to [] if 31 is met
        """
        card_points = [self.value_map['numbers'][val[:-1]]
                       for val in self.r_hist if val != 'GO']
        total = sum(card_points)
        return total
