from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from models.generate_hand_models import GenerateHandModel
from models.generate_peg_models import GeneratePegModel

def compare_distributions(file1, file2, plot_title, saveloc):
    """
    Compares distribution of scores from two files and saves a graph plotting
    the score distributions between the two.

    INPUT: Two file locations, a title for the plot, and the save location
    OUTPUT: Histogram saved to the save location
    """
    df_1 = pd.read_csv(file1)
    df_1_label = file1.split('/')[-2]
    df_2 = pd.read_csv(file2)
    df_2_label = file2.split('/')[-2]
    plt.clf()
    if plot_title == 'Hand Scores':
        bins = range(0,30,1)
    else:
        bins = range(0,10,1)
    weights = np.ones_like(df_1['score'].values) / float(len(df_1['score']))
    df_1['score'].hist(bins=bins, label=df_1_label, weights=weights, alpha=0.5)
    weights = np.ones_like(df_2['score'].values) / float(len(df_2['score']))
    df_2['score'].hist(bins=bins, label=df_2_label, weights=weights, alpha=0.5)
    plt.title('Distribution for %s modeled/trained' % (plot_title))
    plt.legend()
    plt.savefig(saveloc)


def main():
    compare_distributions('data/logs/random/hand_base_table.txt',
                            'data/logs/model/hand_base_table.txt',
                            plot_title='Hand Scores',
                            saveloc='graphs/hand_score_distribution.png')
    compare_distributions('data/logs/random/peg_base_table.txt',
                            'data/logs/model/peg_base_table.txt',
                            plot_title='Peg Scores',
                            saveloc='graphs/peg_score_distribution.png')

    #added if building on ec2
    plt.clf()
    ghm = GenerateHandModel('data/logs/random/hand_base_table.txt')
    ghm.build_cv_graph('graphs/hand_model_cv.png')
    plt.clf()
    gpm = GeneratePegModel('data/logs/random/peg_base_table.txt')
    gpm.build_cv_graph('graphs/peg_model_cv.png')

if __name__ == '__main__':
    main()
