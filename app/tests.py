import unittest
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from gameplay.cribplay import find_legal_moves
import time
import random

class VisitorTest(unittest.TestCase):
    """
    Use Selenium based testing to run through an entire game with random choices
    of legal moves. Primarily tests for errors with the app as users progress
    through the app.
    """
    def setUp(self):
        """
        Initialize webdriver and reset the game session
        """
        self.browser = webdriver.Firefox()
        self.browser.get_cookies()
        self.browser.get('http://127.0.0.1:5000/reset')

    def tearDown(self):
        """
        Quit webdriver, no temporary database setup yet
        """
        self.browser.quit()

    def selectxcards(self, x):
        """
        Helper function used during discard section. Find card elements and
        select two during the initial discard phase
        """
        cards = self.browser.find_elements_by_class_name('discard')
        card_length = len(cards)
        selection = random.sample(range(card_length), x)
        [cards[idx].click() for idx in selection]

    def selectlegalpeg(self):
        """
        Helper function used during the pegging section.  Find card elements,
        extract id's and find legal moves for the user.  Out of those legal
        moves select a random sample from the legal moves
        """
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
        """
        Helper function to submit the page.  Sends data from selection back
        to the server
        """
        self.browser.find_element_by_id('submit-button').click()

    def isdealer(self):
        """
        Function to determine if the user is not the dealer-p1
        INPUT: None
        Output: Boolean - True for if the user is the dealer else False
        """
        self.browser.find_elements_by_id('dealer-p1')
        if len(self.browser.find_elements_by_id('dealer-p1')) == 0:
            return False
        return True

    def check_for_title_on_page(self):
        """
        Helper function, runs the test to make sure every page loads.  Searches
        for the title, and test fails if title does not render
        """
        title = self.browser.find_elements_by_class_name('page-header')
        self.assertEqual(len(title), 1)

    def find_phase(self):
        """
        Find the current phase, helper function to help direct flow when
        running an entire game
        INPUT: None
        OUTPUT: current phase
        """
        title = self.browser.find_elements_by_id('game-phase')
        phase = title[0].text[title[0].text.find(' ') + 1:]
        return phase

    def single_game(self):
        """
        Run a single game, direct flow and execute response functions where
        appropriate.  While the game is not in phase "Game Over," the game
        continues.
        """
        phase = self.find_phase()
        while phase != 'Game Over':
            self.check_for_title_on_page()
            print phase
            phase = self.find_phase()
            if phase == 'Deal':
                self.selectxcards(2)
                self.submitpage()
            elif phase == 'Turn' and self.isdealer() == False:
                self.selectlegalpeg()
                self.submitpage()
            elif phase == 'Pegging':
                self.selectlegalpeg()
                self.submitpage()
            else:
                self.submitpage()

    def test_single_game(self):
        """
        Run a single game, currently tests the title renders on each page
        """
        self.single_game()

    # @unittest.skip('skipping multiple games')
    def test_multiple_games(self, n=5):
        """
        Run multiple games.  Needs testing added to make sure the user log data
        is added to the database.
        """
        for i in range(n):
            print "i is ", i
            self.single_game()


if __name__ == '__main__':
    unittest.main()
