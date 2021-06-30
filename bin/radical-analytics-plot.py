#!/usr/bin/env python3

# ------------------------------------------------------------------------------
#
MAX_LINES   = 0
MAX_SOURCES = 0
N_BINS      = 50

# ------------------------------------------------------------------------------
#
import sys
import optparse

import matplotlib
import matplotlib.pyplot as plt
import radical.analytics as ra
import numpy             as np

plt.style.use(ra.get_style('radical_mpl'))
plt.rcParams['axes.autolimit_mode'] = 'data'

colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
          '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
          '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
          '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
# ------------------------------------------------------------------------------
#
def set_size(width=250, fraction=1, subplots=(1, 1)):
    """ Set aesthetic figure dimensions to avoid scaling in latex.

    Parameters
    ----------
    width   : float
              Width in pts
    fraction: float
              Fraction of the width which you wish the figure to occupy

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

    # figure size in inches
    fig_width_in  = fig_width_pt * inches_per_pt
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return fig_width_in, fig_height_in


# ------------------------------------------------------------------------------
#
TITLE     = ''
DELIM     = None
MATCH     = None
COLUMN_X  = 'count'
COLUMNS_Y = ['1']
LEGEND    = []
LABEL_X   = ''
LABEL_Y   = ''
TICKS_X   = []
TICKS_Y   = []
LOG_X     = False
LOG_Y     = False
LOG       = ''
SIZE      = (13, 8)
STYLE     = 'line'  # 'point', 'line', 'step', 'bar', 'hist'
GRID      = True    # True, False
SAVE_AS   = 'x11'   # 'svg', 'png', 'x11'
FNAME     = ''


# ------------------------------------------------------------------------------
#
def usage(msg=None):

    ret = 0
    if msg:
        print('\n\n\t\tError: %s\n' % msg)
        ret = 1

    print('''

    usage  : radical-analytics-plot [<src>] [options]
    example: radical-analytics-plot experiment.dat -t 'title' --log 'x,y'
    source : space separated data file (read from stdin if not specified)
    options:
        -h, --help                             : this message
        -t, --title      <title>               : plot title
        -X, --x-label    <label>               : x-axis label
        -Y, --y-label    <label>               : y-axis label
        -d, --delim      <char>                : column delimiter
        -m, --match      <pattern>             : use lines matching pattern
        -x, --x-column   <col>                 : source column for x-values
        -y, --y-columns  <col_1,col_2,...>     : list of columns columns to plot
        -L, --legend     <label_1,label_2,...> : name of plots specified in '-y'
        -u, --x-ticks    <tick_1,tick_2,...>   : not yet supported
        -v, --y-ticks    <tick_1,tick_2,...>   : not yet supported
        -s, --style      <point | line | step | bar | hist>
                                               : plot type
        -z, --size       <20,14>               : canvas size
        -l, --log        <x | y | x,y>         : log-scale for x and/or y axis
        -a, --save-as    <png | svg | x11>     : save fig in format (x11: show)
        -f, --filename   <file_name>           : filename base for save (no ext)

''')

    sys.exit(ret)


# ------------------------------------------------------------------------------
# parse options
parser = optparse.OptionParser(add_help_option=False)

parser.add_option('-t', '--title',     dest='title')
parser.add_option('-X', '--x-label',   dest='xlabel')
parser.add_option('-Y', '--y-label',   dest='ylabel')
parser.add_option('-d', '--delimiter', dest='delim')
parser.add_option('-m', '--match',     dest='match')
parser.add_option('-x', '--x-column',  dest='xcol')
parser.add_option('-y', '--y-columns', dest='ycols')
parser.add_option('-u', '--x-ticks',   dest='xticks')
parser.add_option('-v', '--y-ticks',   dest='yticks')
parser.add_option('-L', '--legend',    dest='legend')
parser.add_option('-s', '--style',     dest='style')
parser.add_option('-z', '--size',      dest='size')
parser.add_option('-l', '--log',       dest='log')
parser.add_option('-a', '--save-as',   dest='save')
parser.add_option('-f', '--filename',  dest='fname')
parser.add_option('-h', '--help',      dest='help', action="store_true")

options, args = parser.parse_args()
if len(args) < 1:
    srcs = [None]
else:
    srcs = args[0:]

if options.help   : usage()
if options.title  : TITLE        =  str(options.title)
if options.delim  : DELIM        =  str(options.delim)
if options.match  : MATCH        =  str(options.match)
if options.xcol   : COLUMN_X     =  str(options.xcol)
if options.ycols  : COLUMNS_Y    = [str(x) for x in options.ycols .split(',')]
if options.xlabel : LABEL_X      =  str(options.xlabel)
if options.ylabel : LABEL_Y      =  str(options.ylabel)
if options.xticks : TICKS_X      = [str(x) for x in options.xticks.split(',')]
if options.yticks : TICKS_Y      = [str(x) for x in options.yticks.split(',')]
if options.legend : LEGEND       = [str(x) for x in options.legend.split(',')]
if options.size   : SIZE         = [int(x) for x in options.size  .split(',')]
if options.log    : LOG          =  str(options.log)
if options.style  : STYLE        =  str(options.style)
if options.save   : SAVE_AS      =  str(options.save)
if options.fname  : FNAME        =  str(options.fname)

if 'x' in LOG: LOG_X = True
if 'y' in LOG: LOG_Y = True

if STYLE not in ['point', 'line', 'step', 'bar', 'hist']:
    raise ValueError('invalid style: %s' % STYLE)

if COLUMN_X not in ['count']:
    COLUMN_X = int(COLUMN_X)

if not FNAME:
    FNAME = TITLE.replace('', '_').lower()


# ------------------------------------------------------------------------------
# read and sort data
def get_lines(src):
    if src:
        x = 0
        with open(src, 'r') as fin:
            for line in fin.readlines():
                line = line.strip()
                x += 1
                if MAX_LINES and x >= MAX_LINES:
                    break
                if line:
                    yield line
    else:
        for line in sys.stdin:
            line = line.strip()
            if line:
                yield line


# ------------------------------------------------------------------------------
def get_elems(line):
    if DELIM:
        elems = [e.strip() for e in line.split(DELIM)]
      # print(elems)
    else:
        elems = line.split()

    ret = list()
    for e in elems:
        try:
            ret.append(float(e))
        except:
            ret.append(0.0)

    return ret

plt.figure(figsize=set_size())
plt.locator_params(axis='y', nbins=5)
plt.locator_params(axis='x', nbins=5)

import os
if 'XLIM' in os.environ:
    xmin, xmax = os.environ['XLIM'].split(':')
    xmin = int(xmin)
    xmax = int(xmax)
    plt.xlim(xmin=xmin, xmax=xmax)
if 'YLIM' in os.environ:
    ymin, ymax = os.environ['YLIM'].split(':')
    ymin = int(ymin)
    ymax = int(ymax)
    plt.ylim(ymin=ymin, ymax=ymax)

p_idx = 0

# ------------------------------------------------------------------------------
s = 0
for src in srcs:

    if MAX_SOURCES and s >= MAX_SOURCES:
        break
    s += 1

    print(src)

    rows = list()
    for line in get_lines(src):

        if line.startswith('#'):
          # continue
            elems  = get_elems(line)[1:]
            if not LEGEND:
                LEGEND = [''] * (len(elems))
            for idx in range(len(elems)):
                elem = elems[idx]
                if idx == COLUMN_X:
                    if not LABEL_X:
                        LABEL_X = elem
                else:
                    if not LEGEND:
                        LEGEND[idx] = elem

        else:
            if MATCH and MATCH not in line:
                continue
            rows.append(get_elems(line))

        if not LABEL_X:
            LABEL_X = COLUMN_X

    if not rows:
        raise ValueError('no matching data')

    ZERO_X = True
    if ZERO_X and COLUMN_X != 'count':
        idx = int(COLUMN_X)
        sub = min([row[idx] for row in rows])
        for row in rows:
            row[idx] -= sub

    ZERO_Y = True
    if ZERO_Y:
        for COLUMN_Y in COLUMNS_Y:
            idx = int(COLUMN_Y)
            sub = min([y for y in rows[idx]])
            for row in rows:
                row[idx] -= sub


    # ------------------------------------------------------------------------------
    # invert rows to actual data layout
    data  = list()
    ncols = len(rows[0])
    for idx in range(ncols):
        data.append(list())

    for row in rows:
        for col in range(ncols):
            data[col].append(row[col])

    if STYLE == 'hist':
        if COLUMN_X and COLUMN_X != 'count':
            raise ValueError('histogram plots should specify `-y`, not `-x`')

    # ------------------------------------------------------------------------------
    # plot data
    # pprint.pprint(data)
    try:
        cnum = 0
        for col in COLUMNS_Y:

            if LEGEND: label = LEGEND[p_idx]
            else     : label = None
          # else     : label = str(cnum)

            cnum  += 1
            p_idx += 1

            if COLUMN_X == 'count':
                data_x = list(range(len(data[0])))
            else:
                data_x = np.array(data[COLUMN_X])

            if '+' in col:
                cols = col.split('+', 1)
                cols = [int(cols[0]), int(cols[1])]
                data_y = np.array(data[cols[0]]) + np.array(data[cols[0]])
                data_y = np.array(data[cols[0]]) + np.array(data[cols[1]])

            elif '-' in col:
                cols = col.split('-', 1)
                cols = [int(cols[0]), int(cols[1])]
                data_y = np.array(data[cols[0]]) - np.array(data[cols[0]])

            else:
                scale  = float(os.environ.get('SCALE', 1))
                col    = int(col)
                tmp    = [x * scale for x in data[col]]
                data_y = np.array(tmp)

            color = colors[col]

            if   STYLE == 'point': plt.scatter(data_x, data_y, label=label,
                                               s=10, color=color)
            elif STYLE == 'line' : plt.plot   (data_x, data_y, 'b', label=label,
                                               color=color)
            elif STYLE == 'step' : plt.step   (data_x, data_y, 'b', label=label,
                                               where='post', color=color)
            elif STYLE == 'bar'  : plt.bar    (data_x, data_y, label=label,
                                               color=color)
            elif STYLE == 'hist' :

                if LOG_X:
                    hist, bins, _ = plt.hist(data_y, bins=N_BINS)
                    logbins       = np.logspace(np.log10(bins[0]),
                                                np.log10(bins[-1]), len(bins))
                    plt.hist(data_y, bins=logbins, label=label, histtype='bar',
                             color=color)
                else:
                    if xmin is not None and xmax is not None:
                        bins = list(range(xmin, xmax, N_BINS))
                        plt.hist(data_y, bins=bins, label=label, histtype='bar',
                                 color=color)
                    else:
                        plt.hist(data_y, label=label, histtype='bar',
                                 color=color)

    except IndexError:
        print('index error')
      # for i,e in enumerate(data[0]):
      #     print('    %2d: %s' % (i, e))
        raise

    plt.legend(ncol=2, fancybox=True)  # , loc='upper right')

    # if TITLE   : plt.title(TITLE)
    if LOG_X   : plt.xscale('log')
    if LOG_Y   : plt.yscale('log')
    if LABEL_X : plt.xlabel(LABEL_X)
    if LABEL_Y : plt.ylabel(LABEL_Y)
    if TICKS_X : plt.xticks([int(t) for t in TICKS_X], TICKS_X)
    if TICKS_Y : plt.yticks([int(t) for t in TICKS_Y], TICKS_Y)
    if GRID    : plt.grid(True)

fbase = TITLE.lower()
formats = SAVE_AS.split(',')
if 'png' in formats: plt.savefig('%s.png' % (FNAME), bbox_inches="tight")
if 'svg' in formats: plt.savefig('%s.svg' % (FNAME), bbox_inches="tight")
if 'x11' in formats: plt.show()


# ------------------------------------------------------------------------------

