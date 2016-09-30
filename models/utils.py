from sklearn.base import BaseEstimator, TransformerMixin
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
