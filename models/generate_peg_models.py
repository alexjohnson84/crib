import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.externals import joblib
from matplotlib import pyplot as plt
import time
from utils import ItemSelector, PegFeatureExtractor

class GeneratePegModel(object):

    def __init__(self, path):
        with open(path, 'r') as pbt:
            self.headers = pbt.readline().split(',')
            self.peg_data = []
            cnt = 0
            for line in pbt:
                self.peg_data.append(list(eval(line)))
                cnt += 1
                if cnt == 1000000:
                    break
        self.transform()
        self.scores = []


    def transform(self):
        self.X = self.peg_data
        self.y = np.array([line.pop(5) for line in self.peg_data])

    def build_pipeline(self, X, y):
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
                            ('dtr', DecisionTreeRegressor()),
                            ('rfr', RandomForestRegressor(n_jobs=-1)),
                                ])
        self.dtr.fit(X, y)

    def train_model(self, length):
        X = self.X[:length]
        y = self.y[:length]
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(X, y, test_size=0.33, random_state=42)
        self.build_pipeline(self.X_train, self.y_train)

    def score_model(self, length):
        train_score = self.dtr.score(self.X_train, self.y_train)
        test_score = self.dtr.score(self.X_test, self.y_test)
        self.scores.append([length, train_score, test_score])

    def cross_score_model(self):
        lengths = [10, 100, 1000, 10000, 100000] # 1000000, 2000000, 3000000]#, 10000000]
        start = time.time()
        for length in lengths:
            # import pdb; pdb.set_trace()
            self.train_model(length)
            self.score_model(length)
            print 'for length %s, duration has been %s' % \
                                                (length, time.time() - start)

    def build_cv_graph(self):
        lengths = [score[0] for score in self.scores]
        train = [score[1] for score in self.scores]
        test = [score[2] for score in self.scores]
        with open('graphs/peg_scores.txt', 'w') as sc:
            sc.write(str(self.scores))
        print train, test
        plt.plot(lengths, train, color='Blue', label='Train')
        plt.plot(lengths, test, color='Red', label='Test')
        plt.xlabel('# of datapoints')
        plt.ylabel('r^2 value')
        plt.ylim([-1.5, 1.5])
        plt.xscale('log')
        plt.legend()
        plt.savefig('graphs/cv_scores.png')

    def run_full_model(self, length=None):
        if length is None:
            length = len(self.X)
        self.build_pipeline(self.X[:length], self.y[:length])

    def save_model(self, output_path):
        joblib.dump(self.dtr, output_path)


def main(input_path, output_path):
    ghm = GeneratePegModel(input_path)
    ghm.cross_score_model()
    ghm.build_cv_graph()
    # ghm.save_model(output_path)
    # print "running full model"
    # ghm.run_full_model()
    # print "saving model"
    # ghm.save_model(output_path)

if __name__ == '__main__':
    main('data/peg_base_table.txt', 'models/peg_model/test_model.pkl')
