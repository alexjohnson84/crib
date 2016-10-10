from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
import sys
from models.utils import ItemSelector, PegFeatureExtractor, append_dict_to_file, GenerateModelBaseClass


class GeneratePegModel(GenerateModelBaseClass):
    """
    Generate the peg model object
    """
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


def main(input_path, output_path, cv=False):
    """
    Based on input, we decide if we run cross validations for model comparison,
    or we want to run the model on the entire dataset and store
    """
    ghm = GeneratePegModel(input_path)
    ghm.transform(y_idx=5)
    if cv:
        lengths = [10, 100, 1000, 10000, 100000, 1000000, 2000000, 3000000, 4000000]
        ghm.cv_pipeline_models('graphs/peg_scores.txt', lengths)
        ghm.build_cv_graph('graphs/peg_cv_scores.png',
                            'Pegging Model Performance Across Models',
                            'graphs/peg_scores.txt')
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
