from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from utils.show import scatter_by_column_value
from .calculation_base import CalculationBase


class LDA(CalculationBase):
    def get_transformation(self, group_by_column, indices=None, info=True):
        clf = LinearDiscriminantAnalysis()  # solver='eigen', lsqr, n_components=2
        clf.fit(self.values if indices is None else self.values[indices],
                self.data.column_values_to_idx(group_by_column, indices=indices))
        if info:
            print('Explained variance ratio: ', clf.explained_variance_ratio_)
        return self.make_transformation(clf.transform, 2)
