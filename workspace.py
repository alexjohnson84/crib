import unittest
from decktools import deck_init
import json

test_hands = json.load(open("test_files/test_hands.txt"))

#print(test_hands.values())
a = test_hands["fifteen"]["ex1"]
a = eval(a)
#print(a[1])
def read_hand(hands,ptype,example):
	return(list(hands[ptype].keys()))

print(read_hand(test_hands,"fifteen","ex1"))