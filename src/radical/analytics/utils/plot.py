import os
import sys
import glob


# ------------------------------------------------------------------------------
#
def get_plotsize(width, fraction=1, subplots=(1, 1)):
    """ Set aesthetic figure dimensions to avoid scaling in latex.

    Parameters
    ----------
    width   : float
              Width in points (pts)
    fraction: float
              Fraction of the width which you wish the figure to occupy
    subplots: tuple
              Number of raws and number of columns of the plot

    Returns
    -------
    fig_dim : tuple
              Dimensions of figure in inches
    """
    # Width of figure
    fig_width_pt = width * fraction

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    golden_ratio = (5 ** 0.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt

    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return fig_width_in, fig_height_in

# ------------------------------------------------------------------------------
#
def get_mplstyle(name):

    path  = os.path.dirname(sys.executable)
    path += '/../share/radical.analytics/styles'

    for path in glob.glob('%s/*.txt' % path):
        if path.endswith('/%s.txt' % name):
            return os.path.normpath(path)
