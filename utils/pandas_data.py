"""Base classes for classes that work with pandas data.

Data is of pandas types.
"""
import pandas


class PandasDataFrame:
    def __init__(self, data_frame=None, excel=None, sheetname=None):
        if data_frame:
            self.data_frame = data_frame
        elif excel:
            self.data_frame = pandas.read_excel(excel, sheetname=2)

    def column_unique_values(self, column):
        return sorted(self.data_frame[column].unique())

    def column_values_to_idx(self, column, indices=None):
        data = self.data_frame[column]
        if indices is not None:
            data = data[indices]

        vals = sorted(data.unique())
        map_val = dict((v, i + 1) for i, v in enumerate(vals))
        return [map_val[v] for v in data]

    # ToDo: are needed?
    def get_columns(self):
        return self.data_frame.columns.tolist()

    def get_data_frame(self):
        return self.data_frame
