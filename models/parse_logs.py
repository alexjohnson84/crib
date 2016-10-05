import json
import csv
import os.path
import sys
from models.generate_data import get_highest_file


class BuildBaseTables(object):
    """
    Build base table for a specific log file for both pegging and hand models
    This will be read in multiple times and appended to the csv file
    """

    def __init__(self, input_path):
        """
        Load json file into object
        """
        with open(input_path, 'r') as gl:
            self.logs = json.loads(gl.read())

    def check_for_file(self, path, names):
        """
        If file exists, we want to save the object with the header, else we
        don't want to run it with the header
        INPUT: path, names of columns
        OUPUT: list of headers if file exists, or empty list if does not exist
        """
        if os.path.isfile(path) == False:
            header = names
        else:
            header = []
        return header

    def assemble_hand_base_table(self, output_path):
        """
        Iterate through each game played in the game logs, and extract
        the ['hand', 'score', 'dealer] to be used to build supervised learning
        model
        Each line of the hand base table is the final score, if the user was
        the dealer, and what 4-card hand they got that score with.
        """
        abt = self.check_for_file(output_path, [['hand', 'score', 'dealer']])
        for game_val in self.logs:
            round_nums = sorted([int(key) for key in game_val.keys()])
            prev_score = [0, 0]
            for i in round_nums:
                i = str(i)
                if 'Round Complete' in game_val[i]:
                    hands = game_val[i]['Round Complete']['hands']
                    scores = game_val[i]['Round Complete']['scores']
                    dealer = game_val[i]['Round Complete']['dealer']
                    score_diff = [
                        sc - prevsc for sc,
                        prevsc in zip(
                            scores,
                            prev_score)]
                    prev_score = scores
                    for player in range(2):
                        line = [
                            hands[player],
                            score_diff[player],
                            dealer == player]
                        abt.append(line)
        with open(output_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(abt)

    def assemble_peg_base_table(self, output_path):
        """
        Build peg based table with ['hand', 'cards_played', 'peg_history',
            'len_opponent', 'count', 'score'] and save to output_path

        We extract each round of pegging for each game, and score is tracked as
        the delta of each pegging action. The peg base table with be considerably
        longer than the hand base table due to this
        """
        abt = self.check_for_file(output_path,
                                  [['hand', 'cards_played', 'peg_history',
                                      'len_opponent', 'count', 'score']]
                                  )
        cnt = 0
        for game_val in self.logs:
            round_nums = sorted([int(key) for key in game_val.keys()])
            for i in round_nums:
                i = str(i)
                if 'Round Complete' in game_val[i]:
                    peg_nums = sorted([int(key)
                                       for key in game_val[i]['Pegging'].keys()])
                    prev_score = game_val[i]['Turn']['scores']
                    for j in peg_nums:
                        # import pdb; pdb.set_trace()
                        j = str(j)
                        cnt += 1
                        pegger = game_val[i]['Pegging'][j]['pegger']
                        scores = game_val[i]['Pegging'][j]['scores']
                        score_diff = [
                            sc - prevsc for sc,
                            prevsc in zip(
                                scores,
                                prev_score)]
                        prev_score = scores

                        line = [game_val[i]['Pegging'][j]['hands'][pegger],
                                sum([len(p_hist) for p_hist in game_val[i]
                                     ['Pegging'][j]['peg_phist'].values()]),
                                game_val[i]['Pegging'][j]['peg_hist'],
                                len(game_val[i]['Pegging'][j]['hands'][abs(pegger - 1)]),
                                game_val[i]['Pegging'][j]['peg_count'],
                                score_diff[abs(pegger - 1)]]
                        abt.append(line)
        with open(output_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(abt)


def main(base_dir):
    """
    Iterate through each file in a given directory, and use it to build the
    base table.  Run for both and and peg models
    """
    hf = get_highest_file(base_dir)
    for i in range(hf):
        bt = BuildBaseTables('%s/para_game_%s.txt' % (base_dir, i))
        bt.assemble_hand_base_table('%s/hand_base_table.txt' % (base_dir))
        bt.assemble_peg_base_table('%s/peg_base_table.txt' % (base_dir))


if __name__ == "__main__":
    """
    Argv input used to determine which directory the parse.  True runs on
    randomly generated logs, else we run on logs run on the model.
    """
    if len(sys.argv) > 1:
        arg = bool(sys.argv[1])
    else:
        arg = False
    if arg:
        main('data/logs/random')
    else:
        main('data/logs/model')
