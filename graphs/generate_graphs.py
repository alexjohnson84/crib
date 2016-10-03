import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    df_1['score'].hist(bins=20, label=df_1_label, normed=True)
    df_2['score'].hist(bins=20, label=df_2_label, normed=True)
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

if __name__ == '__main__':
    main()
