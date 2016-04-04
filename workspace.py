from decktools import deck_init
import json
import itertools

value_map = json.load(open("value_map.txt"))

#TODO - Determine in helper function is needed
test_hands = json.load(open("test_files/test_hands.txt"))
def read_hand(hands,ptype,example):
	return(eval(hands[ptype][example]))


#tmp brought in for debug
test_hands = json.load(open("test_files/test_hands.txt"))

def generate_combos(ary):
	output = []
	for i in range(2,len(ary)+1):
		output.append(list(itertools.combinations(ary,i)))
	return list(itertools.chain(*output))



print(generate_combos(read_hand(test_hands,"fifteen","ex2")))