#from decktools import deck_init
import json
import itertools


value_map = json.load(open("value_map.txt"))

#Helper function brought in for debugging
test_hands = json.load(open("test_files/test_hands.txt"))

def read_hand(hands,ptype,example):
	return(eval(hands[ptype][example]))

def generate_combos(ary):
	output = []
	for i in range(2,len(ary)+1):
		output.append(list(itertools.combinations(ary,i)))
	return list(itertools.chain(*output))

#todo - add ispeg methods
def scorehand(ary, turn_up = '', ispeg = False):
	#check for turn_up card - optional arg
	if(turn_up != ''):
		full_hand = ary + turn_up
	else:
		full_hand = ary
	#initate variables
	current_score = 0
	combinations = generate_combos(full_hand)
	#check for fifteens
	for combo in combinations:
		combo_sum = 0
		for card in combo:
			combo_sum += int(value_map['numbers'][card[:-1]])
		#if sum is 15, add 2 to current score
		if combo_sum == 15:
			current_score += 2
	#check for pairs
	for combo in combinations:
		#skip if combo is not equal to 2, avoids duping
		if(len(combo) != 2):
			pass
		else:
			card_vals = [card[:-1] for card in combo]
			pairs = set([x for x in card_vals if card_vals.count(x) == 2])
			current_score += 2 * len(pairs)

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
	#count double & triple runs
	equivalent_straights = [a for a in all_long_straights if len(a) == longest_straight]	
	current_score += longest_straight * len(equivalent_straights)

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
		suit_of_turnup = turn_up[-1]
		if(('J' +  suit_of_turnup) in ary):
			current_score += 1
	return current_score






#print(generate_combos([1,2,3,4,5]))	
#print(generate_combos(read_hand(test_hands,"fifteen","ex1")))
#print(scorehand(read_hand(test_hands,"straight_4","ex1")))