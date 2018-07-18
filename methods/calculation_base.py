import numpy
from itertools import combinations
from utils.show import scatter_by_column_value, scatter_more_by_column_value


class CalculationBase:
    def __init__(self, data, value_columns):
        """
        Parameters
        ----------
        data : PandasDataFrame
        value_columns : list of str
            Columns which are used for calculation

        """
        self.data = data
        self.data_frame = data.get_data_frame()
        self.value_columns = value_columns
        self.values = self.data_frame[value_columns]

    @staticmethod
    def make_transformation(transformation, num_dim):
        def f(ps):
            ps = transformation(ps)
            if ps.shape[1] == num_dim:
                return ps
            if ps.shape[1] > num_dim:
                return ps[:, :num_dim]
            ps_in_d = numpy.zeros((len(ps), num_dim))
            ps_in_d[:, :ps.shape[1]] = ps
            return ps_in_d
        return f

    def get_transformation(self, group_by_column, indices=None, info=True):
        raise NotImplementedError()

    def show_all(self, group_by_column, info=True):
        trans = self.get_transformation(group_by_column, info=info)
        scatter_by_column_value(
            self.data_frame, group_by_column, self.value_columns,
            transformation=trans, info=info)

    def show_pairwise(self, group_by_column, info=True):
        vals = self.data.column_unique_values(group_by_column)
        num_combs = len(vals) * (len(vals) - 1) // 2
        transformations = []
        data_frames = []
        for vs in combinations(vals, 2):
            indices = (self.data_frame[group_by_column] == vs[0]) | \
                (self.data_frame[group_by_column] == vs[1])
            transformations.append(self.get_transformation(
                group_by_column, indices=indices, info=info))
            data_frames.append(self.data_frame[indices])
        #
        scatter_more_by_column_value(
            data_frames, group_by_column, self.value_columns,
            transformations=transformations)
