from decktools import read_hand
import json
import itertools


value_map = json.load(open("value_map.txt"))

#Helper function brought in for debugging
test_hands = json.load(open("test_files/test_hands.txt"))


def generate_combos(ary, ispeg = False):
	output = []
	if(ispeg == False):
		for i in range(2,len(ary)+1):
			output.append(list(itertools.combinations(ary,i)))
		return list(itertools.chain(*output))
	if(ispeg == True):
		for i in range(2, len(ary)+1):
			output.append(tuple(ary[-i:]))
		return list(output)


#todo - add ispeg methods
def scorehand(ary, turn_up = '', ispeg = False):
	#check for turn_up card - optional arg
	if(turn_up != ''):
		full_hand = ary + turn_up
	else:
		full_hand = ary
	#initate variables
	current_score = 0
	combinations = generate_combos(full_hand, ispeg)
	#check for fifteens
	for combo in combinations:
		combo_sum = 0
		for card in combo:
			combo_sum += int(value_map['numbers'][card[:-1]])
		#if sum is 15, add 2 to current score
		if combo_sum == 15:
			current_score += 2
	#check for pairs
	card_vals = [card[:-1] for card in full_hand]
	if(ispeg == False):
		dup_dic = dict((x,card_vals.count(x)) for x in set(card_vals))
		#count_dupes = [dup_dic[x] for x in dup_dic.keys() if dup_dic[x] > 1]
	if(ispeg == True):
		pair_cards = card_vals.pop(-1)
		pair_cards = pair_cards.split()
		for a in card_vals[::-1]:
			if a == pair_cards[0]:
				pair_cards.append(a)
			else:
				break
		dup_dic = dict((x,pair_cards.count(x)) for x in set(pair_cards))		
	count_dupes = [dup_dic[x] for x in dup_dic.keys() if dup_dic[x] > 1]
	pairs_scores = {2 : 2, 3 : 6, 4 : 12}
	for key in pairs_scores.keys():
		for dup_count in count_dupes:

			if key in count_dupes:
				current_score += pairs_scores[key]
	#check for runs
	longest_straight = 0
	longest_straight_cards = []
	all_long_straights = []
	for combo in combinations:
		#skip if combo is greater than 3 and has a potential to be the longest straight
		#main objective here is to find the longest straight, but to double count straights with pairs
		if(len(combo) >= 3 and len(combo) >= longest_straight):

			runtotal = (int(value_map['sequence'][card[:-1]]) for card in combo)
			seq = sorted(list(runtotal))
			#determine if the cards are sequential
			if((seq == list(range(seq[0], seq[-1]+1)))==True):
				all_long_straights.append(combo)
				longest_straight = len(combo)
				longest_straight_cards = combo
	#count double & triple runs if non-peg
	if ispeg == False:
		equivalent_straights = [a for a in all_long_straights if len(a) == longest_straight]
		current_score += longest_straight * len(equivalent_straights)	
	if ispeg == True:
		current_score += longest_straight


	#check for flush
	largest_flush = 0
	for combo in combinations:
		if(len(combo) >= 4):
			suits = [card[-1] for card in combo]
			current_flush = max([suits.count(a) for a in suits])
			if(current_flush >= largest_flush):
				largest_flush = current_flush
	if(largest_flush >= 4 and ispeg == False):
		current_score += largest_flush

	#check for nobs

	if(turn_up != '' and ispeg == False):
		suit_of_turnup = turn_up[-1][-1]
		if(('J' +  suit_of_turnup) in ary):
			current_score += 1
	return current_score

def peg(hand, other_hand, count):
	points = 0
	count += int(value_map['numbers'][hand[0][:-1]])
	if count == 15 or count == 31:
		points += 2
	return [points, hand[1:], hand[0], count]




#print(generate_combos([1,2,3,4,5], True))	
#print(generate_combos(read_hand(test_hands,"fifteen","ex1")))
#print(scorehand(read_hand(test_hands,"handscore","15 point","ex1")))
#print(scorehand(read_hand(test_hands,"handscore","16 point","ex2")))
#print(scorehand(read_hand(test_hands,"pegscore","straight_7","ex1"), '', True))

