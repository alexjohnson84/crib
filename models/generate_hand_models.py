import pandas as pd
from sklearn.feature_extraction import FeatureHasher
from sklearn.cross_validation import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
from matplotlib import pyplot as plt
import time
class GenerateHandModel(object):
    def __init__(self, path):
        self.df = pd.read_csv(path)
        self.scores = []
        self.transform()
        # self.hash_feats()
        # self.train_model(100)
        # self.score_model()

    def transform(self):
        self.df['hand'] = self.df['hand'].apply(lambda x: eval(x))
        self.df['hand'] += self.df['dealer'].apply(lambda x: [str(x)])
        self.df['hand'] = self.df['hand'].apply(lambda x: {key:1 for key in x})
        self.X = self.df['hand'].values
        self.y = self.df['score'].values

    def build_pipeline(self, X, y):
        self.dtr = Pipeline([
            ('feature_hashing', FeatureHasher(input_type='dict')),
            ('dtr', DecisionTreeRegressor())
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
        lengths = [10,100,1000, 10000]
        start = time.time()
        for length in lengths:
            self.train_model(length)
            self.score_model(length)
            print 'for length %s, duration has been %s' % (length, time.time()-start)
    def build_cv_graph(self):
        lengths = [score[0] for score in self.scores]
        train = [score[1] for score in self.scores]
        test = [score[2] for score in self.scores]
        print train, test
        plt.plot(lengths, train, color='Blue', label='Train')
        plt.plot(lengths, test, color = 'Red', label='Test')
        plt.xlabel('# of datapoints')
        plt.ylabel('r^2 value')
        plt.ylim([-1.5, 1.5])
        plt.xscale('log')
        plt.legend()
        plt.savefig('graphs/cv_scores.png')

    def run_full_model(self, length):
        self.build_pipeline(self.X[:length], self.y[:length])



    def save_model(self, output_path):
        joblib.dump(self.dtr, output_path)





def main(input_path, output_path):
    ghm = GenerateHandModel(input_path)
    # ghm.cross_score_model()
    # ghm.build_cv_graph()
    ghm.run_full_model(10000)
    ghm.save_model(output_path)

if __name__ == '__main__':
    main('data/hand_base_table.txt', 'models/hand_model/test_model.pkl')
