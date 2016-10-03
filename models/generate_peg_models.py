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
    """
    Generate the peg model object
    """

    def __init__(self, path):
        """
        Read in data from specific file (the parsed ABT)
        Extract headers and run through transform method.
        Initialize several non-parametric regressors to use to compare
        """
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
        """
        Seperate data into X and Y, pulls "score" from idx 5 to y
        """
        self.y = np.array([line.pop(5) for line in self.peg_data])
        self.X = self.peg_data

    def build_pipeline(self, X, y, mod_name):
        """
        Run pipeline class and featureunion. A feature dictionary is built in
        PegFeatureExtractor() and vectorized in 'transformed feats' section of
        the pipeline.
        Note: model needs to be picked before pipeline is run

        input data is fit to the pipeline
        """
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

    def cross_score_model(self, mod_name):
        """
        Cross validate a specific model accoring to specific predetermined lengths.
        This section takes the longest, so added time logging to track process
        Saves self.scores to file in case process is halted for reference.
        """
        lengths = [10, 100, 1000, 10000, 100000, 1000000, 2000000, 3000000, 4000000] #, 20000000]
        start = time.time()
        for length in lengths:
            self.train_model(length, mod_name)
            self.score_model(length)
            print 'for length %s, duration has been %s' % \
                (length, time.time() - start)
        append_dict_to_file('graphs/peg_scores.txt', {mod_name: self.scores})

    def build_cv_graph(self, fig_loc):
        """
        Build matplotlib line graph comparing train/test data across models and
        saves figure to figlog
        """
        with open('graphs/peg_scores.txt', 'r') as hs:
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

    def cv_pipeline_models(self):
        """
        Cross validate all models for each graph in self.models
        """
        for mod_name in self.models.keys():
            self.scores = []
            self.cross_score_model(mod_name)
        #self.build_cv_graph('graphs/peg_cv_scores.png')


def main(input_path, output_path, cv=False):
    """
    Based on input, we decide if we run cross validations for model comparison,
    or we want to run the model on the entire dataset and store
    """
    ghm = GeneratePegModel(input_path)
    if cv:
        ghm.cv_pipeline_models()
    else:
        ghm.run_full_model('br', 4000000)
        ghm.save_model(output_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = bool(sys.argv[1])
    else:
        arg = False
    main('data/logs/random/peg_base_table.txt',
         'models/peg_model/model.pkl', cv=arg)
