import unittest
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from gameplay.cribplay import find_legal_moves
import time
import random

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.get('http://127.0.0.1:5000/reset')
    def tearDown(self):
        time.sleep(10)
        self.browser.quit()
        pass
    def selectxcards(self, x):
        cards = self.browser.find_elements_by_class_name('discard')
        card_length = len(cards)
        selection = random.sample(range(card_length), x)
        [cards[idx].click() for idx in selection]

    def selectlegalpeg(self):
        pcount = int(self.browser.find_element_by_id('peg-count').text)
        cards = self.browser.find_elements_by_class_name('discard')
        cards_ids = [card.get_attribute('id') for card in cards]
        legal_moves = find_legal_moves(pcount, cards_ids)
        if len(legal_moves) > 0:
            selection = random.sample(legal_moves, 1)[0]
            cards[cards_ids.index(selection)].click()
        else:
            self.submitpage()


    def submitpage(self):
        # time.sleep(2)
        self.browser.find_element_by_id('submit-button').click()


    def check_for_title_on_page(self):
        title = self.browser.find_elements_by_class_name('page-header')
        self.assertEqual(len(title),1)
    def find_phase(self):
        title = self.browser.find_elements_by_id('game-phase')
        phase = title[0].text.split()[1]
        return phase

    def test_gameplay(self):
        phase = self.find_phase()
        print phase
        while phase != 'Game Over':
            self.check_for_title_on_page()
            if phase == 'Deal':
                self.selectxcards(2)
                self.submitpage()
                if len(self.browser.find_elements_by_id('dealer-p1')) == 0:
                    self.selectlegalpeg()
                self.submitpage()
            if phase in ['Pegging']:
                self.selectlegalpeg()
                self.submitpage()
            else:
                self.submitpage()
            phase = self.find_phase()



if __name__ == '__main__':
    unittest.main()
