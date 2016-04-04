from decktools import deck_init
import json
import itertools

value_map = json.load(open("value_map.txt"))

#TODO - Determine in helper function is needed
test_hands = json.load(open("test_files/test_hands.txt"))
def read_hand(hands,ptype,example):
	return(eval(hands[ptype][example]))


def generate_combos(ary):
	output = []
	for i in range(2,len(ary)+1):
		output.append(list(itertools.combinations(ary,i)))
	return list(itertools.chain(*output))

def scorehand(ary):
	current_score = 0
	combinations = generate_combos(ary)
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

		

	return current_score





#print(generate_combos([1,2,3,4,5]))	
#print(generate_combos(read_hand(test_hands,"fifteen","ex1")))
print(scorehand(read_hand(test_hands,"pair","ex2")))