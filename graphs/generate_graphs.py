from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from models.generate_hand_models import GenerateHandModel
from models.generate_peg_models import GeneratePegModel

class PlotDistributions(object):
    def __init__(self):
        self.average_scores = [None, None]
        self.distr = [None, None]
        self.iterations = 100000

    def get_distr_x(self, cnt, bin_vals, const):
        """
        Run a simulation for a specific number of rounds to simulate a full
        game.
        INPUT: counts(proportion), and the bin_vals(point values),
        and const(average number of rounds needed to complete a game)
        OUTPUT: score of game (mean of experimental model should be 120)
        """
        cnt = np.append(cnt, 1-sum(cnt))
        sel = [np.random.choice(bin_vals, p=cnt) for _ in range(int(const))]
        sel.append(np.random.choice(bin_vals, p=cnt) * (const % 1))
        return sum(sel)

    def compare_distributions(self, file1, file2, plot_title, saveloc):
        """
        Compares distribution of scores from two files and saves a graph plotting
        the score distributions between the two for single peg and hand models.
        Also runs the simulation to get the distribution of a full game using
        both models and stores in object.
        Note:  The ABT for the hand_model already includes peg scores.
        We don't do anything with the peg model to run the distribution as it
        was already incoporated when generating data

        INPUT: Two file locations, a title for the plot, and the save location
        OUTPUT: Histogram saved to the save location
        """
        df_1 = pd.read_csv(file1)
        self.df_1_label = file1.split('/')[-2]
        df_2 = pd.read_csv(file2)
        self.df_2_label = file2.split('/')[-2]
        plt.clf()
        if plot_title == 'Hand Scores':
            bins = range(0,40,1)
        else:
            bins = range(0,10,1)
        weights = np.ones_like(df_1['score'].values) / float(len(df_1['score']))
        counts_0, bin_vals_0, _ = plt.hist(df_1['score'], bins=bins, label=self.df_1_label, weights=weights, alpha=0.5)
        self.average_scores[0] = sum([cnt * bv for cnt, bv in zip(counts_0, bin_vals_0[:-1])]) / sum(counts_0)

        weights = np.ones_like(df_2['score'].values) / float(len(df_2['score']))
        counts_1, bin_vals_1, _ = plt.hist(df_2['score'], bins=bins, label=self.df_2_label, weights=weights, alpha=0.5)
        self.average_scores[1] = sum([cnt * bv for cnt, bv in zip(counts_1, bin_vals_1[:-1])]) / sum(counts_1)

        const = 120 / self.average_scores[1]
        if plot_title == 'Hand Scores':
            self.distr[0] = [self.get_distr_x(counts_0, bin_vals_0, const) for _ in range(self.iterations)]
            self.distr[1] = [self.get_distr_x(counts_1, bin_vals_1, const) for _ in range(self.iterations)]
        plt.title('Distribution for %s modeled/trained' % (plot_title))
        plt.legend()
        plt.savefig(saveloc)
    def plot_full_game_distributions(self, saveloc):
        """
        Plot the distributions for full hand.
        """
        bins = range(0,160,1)
        plt.clf()
        for i, label in enumerate([self.df_1_label, self.df_2_label]):
            weights = np.ones_like(self.distr[i]) / float(len(self.distr[i]))
            plt.hist(self.distr[i], label=label, weights=weights, bins=bins, alpha=0.5)
        plt.vlines(90, 0, 0.04, label="SKUNK", colors='#3d3d29')
        plt.vlines(60, 0, 0.04, label="2XSKUNK")
        plt.vlines(120, 0, 0.04, label="Finish Line", colors='#000099')
        plt.ylim(0,0.03)
        plt.title('Distribution for full game')
        plt.legend()
        plt.savefig(saveloc)

def main():
    pd = PlotDistributions()

    pd.compare_distributions('data/logs/random/hand_base_table.txt',
                            'data/logs/model/hand_base_table.txt',
                            plot_title='Hand Scores',
                            saveloc='graphs/hand_score_distribution.png')
    pd.plot_full_game_distributions(saveloc='graphs/full_game_distribution.png')
    pd.compare_distributions('data/logs/random/peg_base_table.txt',
                            'data/logs/model/peg_base_table.txt',
                            plot_title='Peg Scores',
                            saveloc='graphs/peg_score_distribution.png')

    #added if building on ec2
    plt.clf()
    ghm = GenerateHandModel('data/logs/random/hand_base_table.txt')
    ghm.build_cv_graph('graphs/hand_model_cv.png', "Hand Model Comparison")
    plt.clf()
    gpm = GeneratePegModel('data/logs/random/peg_base_table.txt')
    gpm.build_cv_graph('graphs/peg_model_cv.png', "Peg Model Comparison")

if __name__ == '__main__':
    main()
