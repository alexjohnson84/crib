import json
import csv

class BuildBaseTables(object):
    def __init__(self, input_path):
        with open(input_path, 'r') as gl:
            self.logs = json.loads(gl.read())

    def assemble_hand_base_table(self, output_path):
        abt = [['hand', 'score', 'dealer']]
        for game_key, game_val in self.logs.iteritems():
            round_nums = sorted([int(key) for key in game_val.keys()])
            prev_score = [0,0]
            for i in round_nums:
                i = str(i)
                if 'Round Complete' in game_val[i]:
                    hands = game_val[i]['Round Complete']['hands']
                    scores = game_val[i]['Round Complete']['scores']
                    dealer = game_val[i]['Round Complete']['dealer']
                    score_diff = [sc - prevsc for sc, prevsc in zip(scores, prev_score)]
                    prev_score = scores
                    for player in range(2):
                        line = [hands[player], scores_diff[player], dealer == player]
                        abt.append(line)
        with open(output_path ,'w') as f:
            writer = csv.writer(f)
            writer.writerows(abt)

    def assemble_peg_base_table(self, output_path):
        abt = [['hand', 'cards_played', 'peg_history', 'len_opponent', 'count', 'score']]
        for game_key, game_val in self.logs.iteritems():
            round_nums = sorted([int(key) for key in game_val.keys()])
            prev_score = [0,0]
            for i in round_nums:
                i = str(i)
                if 'Round Complete' in game_val[i]:
                    peg_nums = sorted([int(key) for key in game_val[i]['Pegging'].keys()])
                    prev_score = game_val[i]['Turn']['scores']
                    for j in peg_nums:
                        j = str(j)
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
        with open(output_path ,'w') as f:
            writer = csv.writer(f)
            writer.writerows(abt)




if __name__ == "__main__":
    bt = BuildBaseTables('data/game_logs.txt')
    bt.assemble_hand_base_table('data/hand_base_table.txt')
    bt.assemble_peg_base_table('data/peg_base_table.txt')
