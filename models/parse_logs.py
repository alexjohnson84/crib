import json
import csv
import os.path
from models.generate_data import get_highest_file

class BuildBaseTables(object):
    def __init__(self, input_path):
        with open(input_path, 'r') as gl:
            self.logs = eval(gl.read())

    def check_for_file(self, path, names):
        if os.path.isfile(path) == False:
            header = names
        else:
            header = []
        return header

    def assemble_hand_base_table(self, output_path):
        abt = self.check_for_file(output_path, [['hand', 'score', 'dealer']])
        for game_val in self.logs:
            round_nums = sorted([int(key) for key in game_val.keys()])
            prev_score = [0,0]
            for i in round_nums:
                if 'Round Complete' in game_val[i]:
                    hands = game_val[i]['Round Complete']['hands']
                    scores = game_val[i]['Round Complete']['scores']
                    dealer = game_val[i]['Round Complete']['dealer']
                    score_diff = [sc - prevsc for sc, prevsc in zip(scores, prev_score)]
                    prev_score = scores
                    for player in range(2):
                        line = [hands[player], score_diff[player], dealer == player]
                        abt.append(line)
        with open(output_path ,'a') as f:
            writer = csv.writer(f)
            writer.writerows(abt)

    def assemble_peg_base_table(self, output_path):
        abt = self.check_for_file(output_path,
                                    [['hand', 'cards_played', 'peg_history',
                                    'len_opponent', 'count', 'score']]
                                    )

        cnt = 0
        for game_val in self.logs:
            round_nums = sorted([int(key) for key in game_val.keys()])
            for i in round_nums:
                if 'Round Complete' in game_val[i]:
                    peg_nums = sorted([int(key) for key in game_val[i]['Pegging'].keys()])
                    prev_score = game_val[i]['Turn']['scores']
                    for j in peg_nums:
                        # j = str(j)
                        cnt += 1
                        pegger = game_val[i]['Pegging'][j]['pegger']
                        scores = game_val[i]['Pegging'][j]['scores']
                        score_diff = [sc - prevsc for sc, prevsc in zip(scores, prev_score)]
                        prev_score = scores

                        line = [game_val[i]['Pegging'][j]['hands'][pegger],
                                   sum([len(p_hist) for p_hist in game_val[i]
                                            ['Pegging'][j]['peg_phist'].values()]),
                                   game_val[i]['Pegging'][j]['peg_hist'],
                                   len(game_val[i]['Pegging'][j]['hands'][abs(pegger-1)]),
                                   game_val[i]['Pegging'][j]['peg_count'],
                                   score_diff[pegger]]
                        abt.append(line)
        with open(output_path ,'a') as f:
            writer = csv.writer(f)
            writer.writerows(abt)

def main(base_dir):
    hf = get_highest_file(base_dir)
    for i in range(hf):
        bt = BuildBaseTables('%s/para_game_%s.txt' % (base_dir, i))
        bt.assemble_hand_base_table('%s/../hand_base_table.txt' % (base_dir))
        bt.assemble_peg_base_table('%s/../peg_base_table.txt' % (base_dir))





if __name__ == "__main__":
    main('data/logs')
    # bt = BuildBaseTables('data/para_game_0.txt')
    # bt.assemble_hand_base_table('data/hand_base_table.txt')
