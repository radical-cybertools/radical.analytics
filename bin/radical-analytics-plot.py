#!/usr/bin/env python


import sys
import time
import optparse

import numpy             as np
import matplotlib        as mpl
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------------
# Global configurations
# ----------------------------------------------------------------------------
# matplotlib style
plt.style.use('seaborn-ticks')

# use LaTeX and its body font for the diagrams' text.
mpl.rcParams['text.usetex'] = True

# mpl.rcParams['text.latex.unicode'] = True
mpl.rcParams['font.serif']  = ['Nimbus Roman Becker No9L']
# mpl.rcParams['font.family'] = 'serif'


# font sizes
SIZE = 24
plt.rc('font'  , size      = SIZE    )
plt.rc('axes'  , titlesize = SIZE    )
plt.rc('axes'  , labelsize = SIZE    )
plt.rc('xtick' , labelsize = SIZE    )
plt.rc('ytick' , labelsize = SIZE    )
plt.rc('legend', fontsize  = SIZE - 2)
plt.rc('figure', titlesize = SIZE    )

# thinner lines for axes to avoid distractions.
mpl.rcParams['axes.linewidth']    = 0.75
mpl.rcParams['xtick.major.width'] = 0.75
mpl.rcParams['xtick.minor.width'] = 0.75
mpl.rcParams['ytick.major.width'] = 0.75
mpl.rcParams['ytick.minor.width'] = 0.75
mpl.rcParams['lines.linewidth']   = 2

# do not use a box for the legend to avoid distractions.
mpl.rcParams['legend.frameon'] = False

# restore part of matplotlib 1.5 behavior
mpl.rcParams['patch.force_edgecolor'] = True
mpl.rcParams['patch.edgecolor']       = 'black'
mpl.rcParams['errorbar.capsize']      = 3

# Use coordinated colors. These are the "Tableau 20" colors as
# RGB. Each pair is strong/light. For a theory of color
tableau20 = [( 31, 119, 180), (174, 199, 232),  # blue        [ 0,1 ]
             (255, 127,  14), (255, 187, 120),  # orange      [ 2,3 ]
             ( 44, 160,  44), (152, 223, 138),  # green       [ 4,5 ]
             (214,  39,  40), (255, 152, 150),  # red         [ 6,7 ]
             (148, 103, 189), (197, 176, 213),  # purple      [ 8,9 ]
             (140,  86,  75), (196, 156, 148),  # brown       [10,11]
             (227, 119, 194), (247, 182, 210),  # pink        [12,13]
             (188, 189,  34), (219, 219, 141),  # yellow      [14,15]
             ( 23, 190, 207), (158, 218, 229),  # cyan        [16,17]
             ( 65,  68,  81), ( 96,  99, 106),  # gray        [18,19]
             (127, 127, 127), (143, 135, 130),  # gray        [20,21]
             (165, 172, 175), (199, 199, 199),  # gray        [22,23]
             (207, 207, 207)]                   # gray        [24]

# Scale the RGB values to the [0, 1] range, which is the format
# matplotlib accepts.
for i in range(len(tableau20)):
    r, g, b = tableau20[i]
    tableau20[i] = (round(r / 255.,1), round(g / 255.,1), round(b / 255.,1))


# Return a single plot without right and top axes, spanning one column text.
def fig_setup(figsize=None):

    if not figsize:
        figsize = (13,7)

    fig = plt.figure(figsize=figsize)
    ax  = fig.add_subplot(111)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    return fig, ax


# ------------------------------------------------------------------------------
#
TITLE     = ''
DELIM     = ''
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
SIZE      = (20, 14)
STYLE     = 'line'  # 'point', 'line', 'step', 'bar', 'hist'
GRID      = True    # True, False
FNAME     = None
SAVE_AS   = 'x11'   # 'svg', 'png', 'x11'


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
        -f, --file-name  <filename>            : name to save to (w/o ext)

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
parser.add_option('-f', '--file-name', dest='fname')
parser.add_option('-h', '--help',      dest='help', action="store_true")

options, args = parser.parse_args()
if len(args) > 1:
    usage("Too many arguments (%s)" % args)

if len(args) < 1:
    src = None
else:
    src = args[0]

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

if COLUMN_X not in ['count']:
    COLUMN_X = int(COLUMN_X)

if SAVE_AS not in ['x11', 'png', 'svg']:
    raise ValueError('invalid save_as value: %s' % SAVE_AS)

if STYLE not in ['point', 'line', 'step', 'bar', 'hist']:
    raise ValueError('invalid style: %s' % STYLE)


# ------------------------------------------------------------------------------
# read and sort data
def get_lines():
    if src:
        with open(src, 'r') as fin:
            for line in fin.readlines():
                line = line.strip()
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
    else:
        elems = line.split()

    ret = list()
    for e in elems:
        try:
            ret.append(float(e))
        except:
            ret.append(e)

    return ret


# ------------------------------------------------------------------------------
rows = list()
for line in get_lines():

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

    fig, ax = fig_setup()
    cnum    = 0
    for col in COLUMNS_Y:

        if LEGEND: label = LEGEND[cnum]
        else     : label = str(cnum)
        cnum += 1

        if COLUMN_X == 'count':
            data_x = list(range(len(data[0])))
        else:
            data_x = np.array(data[COLUMN_X])

        if '+' in col:
            cols = col.split('+', 1)
            cols = [int(cols[0]), int(cols[1])]
            data_y = np.array(data[cols[0]]) + np.array(data[cols[0]])

        elif '-' in col:
            cols = col.split('-', 1)
            cols = [int(cols[0]), int(cols[1])]
            data_y = np.array(data[cols[0]]) - np.array(data[cols[0]])

        else:
            col = int(col)
            time.sleep(1)
            data_y = np.array(data[col])

        if   STYLE == 'point': ax.scatter(data_x, data_y, label=label, s=10)
        elif STYLE == 'line' : ax.plot   (data_x, data_y, 'b', label=label)
        elif STYLE == 'step' : ax.step   (data_x, data_y, 'b', label=label)
        elif STYLE == 'bar'  : ax.bar    (data_x, data_y, label=label)
        elif STYLE == 'hist' : ax.hist   (data_y,  150,   label=label)

except IndexError:
    print('index error')
    for i,e in enumerate(data[0]):
        print('    %2d: %s' % (i, e))
    raise

if LEGEND != ['-']:
    print('===', LEGEND)
    plt.legend(ncol=2, fancybox=True, loc='lower right')

if TITLE   : ax.set_title(TITLE)
if LOG_X   : ax.set_xscale('log')
if LOG_Y   : ax.set_yscale('log')
if LABEL_X : ax.set_xlabel(LABEL_X)
if LABEL_Y : ax.set_ylabel(LABEL_Y)
if TICKS_X : ax.set_xticks([int(t) for t in TICKS_X], TICKS_X)
if TICKS_Y : ax.set_yticks([int(t) for t in TICKS_Y], TICKS_Y)
if GRID    : ax.grid(True)

if not FNAME:
    FNAME = TITLE.lower().replace(' ', '_')
if   SAVE_AS == 'png': fig.savefig('%s.png' % FNAME, bbox_inches="tight")
elif SAVE_AS == 'svg': fig.savefig('%s.svg' % FNAME, bbox_inches="tight")
elif SAVE_AS == 'x11': fig.show()


# ------------------------------------------------------------------------------

