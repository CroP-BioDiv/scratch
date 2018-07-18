"""Methods for displaying common data.
Uses matplotlib library.
Data is mostly numpy arrays or of pandas types.
"""

import math
from itertools import cycle
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


def _scatter_cv(
        ax, data_frame, group_by_column, plot_columns,
        transformation=None, colors='bgrcmyk', markers=None, info=True):
    ax.grid(True, which='both')
    column = data_frame[group_by_column]
    values = data_frame[plot_columns]
    if info:
        print('Number of points: {}'.format(len(values)))
    for val, color, marker in zip(column.unique(), cycle(colors), cycle(markers or 'o')):
        points = values[column == val]
        if info:
            print('  {}: {}'.format(val, len(points)))
        if transformation:
            points = transformation(points)
        x, y = zip(*points)
        ax.scatter(x, y, s=60, edgecolors=color, c=color, label=val, marker=marker)
    ax.legend()


def scatter_by_column_value(
        data_frame, group_by_column, plot_columns,
        transformation=None, colors='bgrcmyk', info=True):
    """
    Shows scatter plot of pandas data_frame marked by defined column value.

    Parameters
    ----------
    data_frame : pandas DataFrame
        Data
    group_by_column : str
        Column name by which values grouping is done
    plot_columns : list of str
        Column names which values are displayed
    transformation : None or callable
        If set, used to transform points before displaying
    colors : iterable
        Colors to use

    """
    fig, ax = plt.subplots()
    _scatter_cv(
        ax, data_frame, group_by_column, plot_columns,
        transformation=transformation, colors=colors, info=True)
    # ax.grid(True, which='both')
    # column = data_frame[group_by_column]
    # values = data_frame[plot_columns]
    # if info:
    #     print('Number of points: {}'.format(len(values)))
    # for val, color in zip(column.unique(), cycle(colors)):
    #     points = values[column == val]
    #     if info:
    #         print('  {}: {}'.format(val, len(points)))
    #     if transformation:
    #         points = transformation(points)
    #     x, y = zip(*points)
    #     ax.scatter(x, y, s=60, edgecolors=color, c=color, label=val)
    # ax.legend()
    plt.show()


def _find_tiles_size(num_plots):
    s = math.ceil(math.sqrt(num_plots))
    if s > 1 and s * s - 1 <= num_plots:
        return s - 1, s + 1
    if (s - 2) * s <= num_plots:
        return s - 2, s
    if (s - 1) * s <= num_plots:
        return s - 1, s
    return s, s


def scatter_more_by_column_value(
        data_frames, group_by_column, plot_columns,
        transformations=None, colors='bg', markers='^v', info=True,
        titles=None):
    #
    size = _find_tiles_size(len(data_frames))
    if not transformations:
        transformations = [None] * len(data_frames)
    if not titles:
        titles = [None] * len(data_frames)
    for i, (df, tran, title) in enumerate(zip(data_frames, transformations, titles)):
        ax = plt.subplot(*size, i + 1)
        _scatter_cv(
            ax, df, group_by_column, plot_columns,
            transformation=tran, colors=colors, markers=markers, info=True)
        if title:
            plt.title(title)
        plt.grid(True)
    plt.show()
