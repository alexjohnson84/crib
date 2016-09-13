import itertools
from collections import Counter

class CribScore(object):
    """
    Score cribbage hand for both cases of pegging and handscoring
    """
    def __init__(self, score_type='hand'):
        """
        Initialize class
        """
        self.score_type = score_type
    def score(self, hand, turn=None):
        """
        Score then hand based upon the scoring type

        Create a counter of values and of suits
        """
        self.hand = hand
        self.turn = turn
        if self.turn is not None:
            self.full_hand = hand + turn
        else:
            self.full_hand = hand
        with open('gameplay/reference_files/value_map.txt', 'r') as vm:
            self.value_map = eval(vm.read())
        self.value_counter = Counter([card[:-1] for card in self.full_hand])
        self.suit_counter = Counter([card[-1] for card in self.full_hand])

        score = 0
        score += self._score_fifteens()
        score += self._score_pairs()
        score += self._score_flushes()
        score += self._score_runs()
        score += self._score_nobs()

        return score

    def _score_fifteens(self):
        current_score = 0
        combos = []
        for i in range(2,len(self.full_hand)+1):
            combos += list(itertools.combinations(self.full_hand,i))
        for cards in combos:
            combo_sum = 0
            for card in cards:
                combo_sum += int(self.value_map['numbers'][card[:-1]])
            if combo_sum == 15:
                current_score += 2
        return current_score


    def _score_pairs(self):
        mapped_pair = {2:2, 3:6, 4:12}
        mapped_values = [mapped_pair[value] for value in self.value_counter.values() \
                                            if value >= 2]
        return sum(mapped_values)
        return sum()
    def _score_flushes(self):
        return sum([value for key, value in self.suit_counter.iteritems() \
                                            if value >= 4])
    def _score_runs(self):
        """
        Map values to the item in sequence, sort, and find longest consecutive
        sequence
        """
        sequence_counter = {self.value_map['sequence'][key]:value \
                                for key, value in self.value_counter.iteritems()}
        sort_seq_keys = sequence_counter.keys()
        longest_sequence = self._longest_consecutive_sequence(sort_seq_keys)

        if len(longest_sequence) >= 3:
            run_counter = [value for key, value in sequence_counter.iteritems()\
                                                    if key in longest_sequence]
            mult_factor = reduce(lambda x,y: x * y, run_counter)
            return len(longest_sequence) * mult_factor
        else:
            return 0

    def _longest_consecutive_sequence(self, lst):
        s_lst = sorted(lst)
        longest_list = [s_lst[0]]
        current_list = [s_lst[0]]
        for i in range(1,len(s_lst)):
            if s_lst[i-1] + 1 == s_lst[i]:
                current_list.append(s_lst[i])
            else:
                current_list = [s_lst[i]]
            if len(current_list) > len(longest_list):
                longest_list = current_list
        return longest_list

    def _score_nobs(self):
        current_score = 0
        if self.turn != None:
            flipped_suit = self.turn[0][-1]
            if "J" + flipped_suit in self.hand:
                current_score += 1
        return current_score
