import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.externals import joblib
from matplotlib import pyplot as plt
import seaborn as sns
import time
import sys
from models.utils import ItemSelector, PegFeatureExtractor, append_dict_to_file
from collections import OrderedDict

class GeneratePegModel(object):

    def __init__(self, path):
        with open(path, 'r') as pbt:
            self.headers = pbt.readline().split(',')
            self.peg_data = []
            for line in pbt:
                self.peg_data.append(list(eval(line)))
        self.transform()
        self.scores = []
        self.models = {'dtr': DecisionTreeRegressor(),
                    'br': BaggingRegressor(n_jobs=-1),
                    'rfr': RandomForestRegressor(n_jobs=-1),
                }

    def transform(self):
        self.X = self.peg_data
        self.y = np.array([line.pop(5) for line in self.peg_data])

    def build_pipeline(self, X, y, mod_name):
        self.dtr = Pipeline([
                            ('featureextract', PegFeatureExtractor()),
                            ('union', FeatureUnion(
                                transformer_list=[
                                        ('pegcount', ItemSelector(key='X_cnt')),
                                        ('opponentlength', ItemSelector(key='X_lo')),
                                        ('cardsplayed', ItemSelector(key='X_cp')),
                                        ('transformed_feats', Pipeline([
                                                    ('selector', ItemSelector(key='X_dict')),
                                                    ('vect', DictVectorizer())
                                                ]))
                                            ])),
                            ('mod', self.models[mod_name])
                            ])
        self.dtr.fit(X, y)

    def train_model(self, length, mod_name):
        X = self.X[:length]
        y = self.y[:length]
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(X, y, test_size=0.33, random_state=42)
        self.build_pipeline(self.X_train, self.y_train, mod_name)

    def score_model(self, length):
        train_score = self.dtr.score(self.X_train, self.y_train)
        test_score = self.dtr.score(self.X_test, self.y_test)
        self.scores.append([length, train_score, test_score])

    def cross_score_model(self, mod_name):
        lengths = [10, 100, 1000]
        start = time.time()
        for length in lengths:
            self.train_model(length, mod_name)
            self.score_model(length)
            print 'for length %s, duration has been %s' % \
                                                (length, time.time() - start)
        append_dict_to_file('graphs/peg_scores.txt', {mod_name:self.scores})


    def build_cv_graph(self, fig_loc):
        with open('graphs/peg_scores.txt', 'r') as hs:
            data = eval(hs.read())
        color_list = ['red', 'green', 'blue']
        color_dict = {key:color_list[i] for i, key in enumerate(sorted(data.keys()))}
        for key, value in data.iteritems():
            x = [point[0] for point in value]
            y = [point[1:] for point in value]
            plt.plot(x, y, label=key, color=color_dict[key])
        plt.xlabel('# of datapoints')
        plt.ylabel('r^2 value')
        plt.ylim([-0.5, 1.1])
        plt.xscale('log')
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        legend = plt.legend(by_label.values(), by_label.keys(), loc=2, frameon=True)
        frame = legend.get_frame()
        frame.set_facecolor('white')
        plt.savefig(fig_loc)

    def run_full_model(self, mod_name, length=None):
        if length is None:
            length = len(self.X)
        self.build_pipeline(self.X[:length], self.y[:length], mod_name)

    def save_model(self, output_path):
        joblib.dump(self.dtr, output_path)

    def cv_pipeline_models(self):
        for mod_name in self.models.keys():
            self.scores = []
            self.cross_score_model(mod_name)
        self.build_cv_graph('graphs/peg_cv_scores.png')

def main(input_path, output_path, cv=False):
    ghm = GeneratePegModel(input_path)
    if cv == True:
        ghm.cv_pipeline_models()
    else:
        ghm.run_full_model('br', 1000)
        ghm.save_model(output_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = bool(sys.argv[1])
    else:
        arg = False
    main('data/logs/random/peg_base_table.txt', 'models/peg_model/model.pkl', cv=arg)
