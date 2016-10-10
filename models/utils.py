from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.externals import joblib
from matplotlib import pyplot as plt
import seaborn as sns
from collections import OrderedDict
import time
import numpy as np
import os


def append_dict_to_file(path, d):
    """
    Function to append a dictionary to a file, used in hand and peg model
    generation
    INPUT: Path, dictionary
    OUTPUT: None
    """
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = eval(f.read())
            data = dict(data.items() + d.items())
    else:
        data = d
    with open(path, 'w') as f:
        f.write(str(data))


class ItemSelector(BaseEstimator, TransformerMixin):
    """
    Note: Taken from http://scikit-learn.org/stable/auto_examples/hetero_feature_union.html#example-hetero-feature-union-py
    For data grouped by feature, select subset of data at a provided key.

    The data is expected to be stored in a 2D data structure, where the first
    index is over features and the second is over samples.  i.e.

    >> len(data[key]) == n_samples

    Please note that this is the opposite convention to sklearn feature
    matrixes (where the first index corresponds to sample).

    ItemSelector only requires that the collection implement getitem
    (data[key]).  Examples include: a dict of lists, 2D numpy array, Pandas
    DataFrame, numpy record array, etc.

    >> data = {'a': [1, 5, 2, 5, 2, 8],
               'b': [9, 4, 1, 4, 1, 3]}
    >> ds = ItemSelector(key='a')
    >> data['a'] == ds.transform(data)

    ItemSelector is not designed to handle data grouped by sample.  (e.g. a
    list of dicts).  If your data is structured this way, consider a
    transformer along the lines of `sklearn.feature_extraction.DictVectorizer`.

    Parameters
    ----------
    key : hashable, required
        The key corresponding to the desired value in a mappable.
    """

    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]


class PegFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Custom Class to create a dict of numpy arrays to be acted upon by ItemSelector
    Input: ABT of form ['hand', 'cards_played', 'peg_history', 'len_opponent', 'count']
    Output:
    dict of keys for features
    'X_dict' = list of dicts with dictvectorized hashing
    'X_cnt' = current count of peg round
    'X_lo' = length of opponents hand
    'X_cp' = length of cards played

    """
    headers = ['hand', 'cards_played', 'peg_history', 'len_opponent', 'count']
    continous = ['cards_played', 'len_opponent', 'count']

    def fit(self, x, y=None):
        return self

    def _line_to_dict(self, headers, line, cont=[]):
        output_dict = {}
        for head, item in zip(headers, line):
            if head in cont:
                pass
            else:
                if isinstance(item, str):
                    item = eval(item)
                if isinstance(item, list):
                    if head == 'hand':
                        for card in item:
                            output_dict[head + "_" + card] = 1
                    elif head == 'peg_history':
                        for i, card in enumerate(item):
                            output_dict[head + "_" + card] = i + 1
                else:
                    output_dict[head] = item
        return output_dict

    def transform(self, peg_data):
        features = {}
        features['X_dict'] = [
            self._line_to_dict(
                self.headers,
                line,
                cont=self.continous) for line in peg_data]
        features['X_cnt'] = np.array([float(line[4])
                                      for line in peg_data]).reshape(-1, 1)
        features['X_lo'] = np.array([float(line[3])
                                     for line in peg_data]).reshape(-1, 1)
        features['X_cp'] = np.array([float(line[1])
                                     for line in peg_data]).reshape(-1, 1)

        return features


class HandFeatureExtractor(BaseEstimator, TransformerMixin):
    """
    Custom Class to create a dict of numpy arrays to be acted upon by ItemSelector
    Input: ABT of form ['hand', 'cards_played', 'peg_history', 'len_opponent', 'count']
    Output:
    dict of keys for features
    'X_dict' = list of dicts with dictvectorized hashing
    'X_cnt' = current count of peg round
    'X_lo' = length of opponents hand
    'X_cp' = length of cards played

    """
    headers = ['hand', 'dealer']

    def fit(self, x, y=None):
        return self

    def transform(self, hand_data):
        features = {}
        features['X_hand'] = [
            {card: 1 for card in eval(line[0])} for line in hand_data]
        features['X_dealer'] = np.array(
            [line[1] for line in hand_data]).reshape(-1, 1)
        return features

class GenerateModelBaseClass(object):
    """
    Generate the peg model object
    """

    def __init__(self, path):
        """
        Read in data from specific file (the parsed ABT)
        Extract headers and run through transform method.
        Initialize several non-parametric regressors to use to compare
        """
        with open(path, 'r') as bt:
            self.headers = bt.readline().split(',')
            self.data = []
            for line in bt:
                self.data.append(list(eval(line)))
        self.scores = []
        self.models = {'dtr': DecisionTreeRegressor(),
                       'br': BaggingRegressor(n_jobs=-1),
                       'rfr': RandomForestRegressor(n_jobs=-1),
                       }

    def transform(self, y_idx):
        """
        Seperate data into X and Y, pulls "score" from idx 1 to y
        """
        self.y = [row.pop(y_idx) for row in self.data]
        self.X = self.data

    def train_model(self, length, mod_name):
        """
        Split X and y based on preset length, then split further into train/test.
        Train model with training set
        """
        X = self.X[:length]
        y = self.y[:length]
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(X, y, test_size=0.33, random_state=42)
        self.build_pipeline(self.X_train, self.y_train, mod_name)

    def score_model(self, length):
        """
        To be run after train_model. Builds R^2 score and creates a list of
        length and scores for graphing
        """
        train_score = self.dtr.score(self.X_train, self.y_train)
        test_score = self.dtr.score(self.X_test, self.y_test)
        self.scores.append([length, train_score, test_score])

    def cross_score_model(self, mod_name, output_file, lengths):
        """
        Cross validate a specific model accoring to specific predetermined lengths.
        This section takes the longest, so added time logging to track process
        Saves self.scores to file in case process is halted for reference.
        """
        start = time.time()
        for length in lengths:
            self.train_model(length, mod_name)
            self.score_model(length)
            print 'for length %s, duration has been %s' % \
                (length, time.time() - start)
        append_dict_to_file(output_file, {mod_name: self.scores})

    def build_cv_graph(self, fig_loc, plot_title, input_score_file):
        """
        Build matplotlib line graph comparing train/test data across models and
        saves figure to figlog
        """
        with open(input_score_file, 'r') as hs:
            data = eval(hs.read())
        color_list = ['red', 'green', 'blue']
        color_dict = {key: color_list[i]
                      for i, key in enumerate(sorted(data.keys()))}
        for key, value in data.iteritems():
            x = [point[0] for point in value]
            y = [point[1:] for point in value]
            plt.plot(x, y, label=key, color=color_dict[key])
        plt.xlabel('# of datapoints')
        plt.ylabel('r^2 value')
        plt.ylim([-0.5, 1.1])
        plt.xscale('log')
        plt.title(plot_title)
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        legend = plt.legend(
            by_label.values(),
            by_label.keys(),
            loc=2,
            frameon=True)
        frame = legend.get_frame()
        frame.set_facecolor('white')
        plt.savefig(fig_loc)

    def run_full_model(self, mod_name, length=None):
        """
        Run full model accoring to length set without splitting into train/test
        """
        if length is None:
            length = len(self.X)
        self.build_pipeline(self.X[:length], self.y[:length], mod_name)

    def save_model(self, output_path):
        """
        Save current model to output_path
        """
        joblib.dump(self.dtr, output_path)
    def cv_pipeline_models(self, output_file, lengths):
        """
        Cross validate all models for each graph in self.models
        """
        for mod_name in self.models.keys():
            self.scores = []
            self.cross_score_model(mod_name, output_file, lengths)
