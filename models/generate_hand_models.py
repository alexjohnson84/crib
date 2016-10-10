from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
import sys
from models.utils import ItemSelector, HandFeatureExtractor, append_dict_to_file, GenerateModelBaseClass


class GenerateHandModel(GenerateModelBaseClass):
    """
    Generate the peg model object
    """
    def build_pipeline(self, X, y, mod_name):
        """
        Run Pipeline class, feature unions on boolean for is dealer, and
        vectorized user hand and runs for named model
        """
        self.dtr = Pipeline([
            ('featureextract', HandFeatureExtractor()),
            ('union', FeatureUnion(
                transformer_list=[
                    ('isdealer', ItemSelector(key='X_dealer')),
                    ('hand', Pipeline([
                        ('selector', ItemSelector(key='X_hand')),
                        ('vect', DictVectorizer())
                    ]))
                ])),
            ('mod', self.models[mod_name])
        ])
        self.dtr.fit(X, y)


def main(input_path, output_path, cv=False):
    """
    Based on input, we decide if we run cross validations for model comparison,
    or we want to run the model on the entire dataset and store
    """
    ghm = GenerateHandModel(input_path)
    ghm.transform(y_idx=1)
    if cv:
        lengths = [10, 100, 1000, 10000, 100000, 1000000, 2500000, 4497780]
        ghm.cv_pipeline_models('graphs/hand_scores.txt', lengths)
        ghm.build_cv_graph('graphs/hand_cv_scores.png',
                            'Hand Model Performance Across Models',
                            'graphs/hand_scores.txt')
    else:
        ghm.run_full_model('br')
        ghm.save_model(output_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = bool(sys.argv[1])
    else:
        arg = False
    main('data/logs/random/hand_base_table.txt',
         'models/hand_model/model.pkl', cv=arg)
