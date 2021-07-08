#!/usr/bin/env python


import sys
import time
import optparse

import numpy             as np
import matplotlib.pyplot as plt
import radical.analytics as ra

from radical.analytics.utils import to_latex


# ----------------------------------------------------------------------------
#
plt.style.use(ra.get_mplstyle("radical_mpl"))


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
RANGE     = [None, None, None, None]
LOG_X     = False
LOG_Y     = False
LOG       = ''
STYLE     = 'line'  # 'point', 'line', 'step', 'bar', 'hist'
GRID      = False   # True, False
FNAME     = None
SAVE_AS   = 'x11'   # 'svg', 'png', 'x11', 'pdf'
WIDTH     = 500


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
        -r, --range      <xmin,xmax,ymin,ymax> : axis range
        -s, --style      <point | line | step | bar | hist>
                                               : plot type
        -w, --width      <252>                 : canvas width
        -l, --log        <x | y | x,y>         : log-scale for x and/or y axis
        -g, --grid                             : grid lines (default: no)
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
parser.add_option('-r', '--range',     dest='range')
parser.add_option('-L', '--legend',    dest='legend')
parser.add_option('-s', '--style',     dest='style')
parser.add_option('-w', '--width',     dest='width')
parser.add_option('-l', '--log',       dest='log')
parser.add_option('-g', '--grid',      dest='grid', action='store_true')
parser.add_option('-a', '--save-as',   dest='save')
parser.add_option('-f', '--file-name', dest='fname')
parser.add_option('-h', '--help',      dest='help', action='store_true')

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
if options.width  : WIDTH        =  int(options.width)
if options.log    : LOG          =  str(options.log)
if options.grid   : GRID         =  str(options.grid)
if options.style  : STYLE        =  str(options.style)
if options.save   : SAVE_AS      =  str(options.save)
if options.fname  : FNAME        =  str(options.fname)

if options.range  :
    RANGE = options.range .split(',')
    RANGE = [float(x) if x else None for x in RANGE]

LEGEND  = [s.strip() for s in LEGEND]
TICKS_X = [s.strip() for s in TICKS_X]
TICKS_Y = [s.strip() for s in TICKS_Y]

if 'x' in LOG: LOG_X = True
if 'y' in LOG: LOG_Y = True

if COLUMN_X not in ['count']:
    COLUMN_X = int(COLUMN_X)

if SAVE_AS not in ['x11', 'png', 'svg', 'pdf']:
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

    fig, ax = plt.subplots(figsize=ra.get_plotsize(WIDTH))
    cnum    = 0
    for col in COLUMNS_Y:

        if LEGEND: label = to_latex(LEGEND[cnum])
        else     : label = to_latex(str(cnum))
        cnum += 1

        if COLUMN_X == 'count':
            data_x = list(range(len(data[0])))
        else:
            data_x = np.array(data[COLUMN_X])

        if '+' in col:
            cols = col.split('+', 1)
            cols = [int(cols[0]), int(cols[1])]
            data_y = np.array(data[cols[0]]) + np.array(data[cols[1]])

        elif '-' in col:
            cols = col.split('-', 1)
            cols = [int(cols[0]), int(cols[1])]
            data_y = np.array(data[cols[0]]) - np.array(data[cols[1]])

        elif '*' in col:
            cols = col.split('*', 1)
            cols = [int(cols[0]), int(cols[1])]
            data_y = np.array(data[cols[0]]) * np.array(data[cols[1]])

        elif '/' in col:
            cols = col.split('/', 1)
            cols = [int(cols[0]), int(cols[1])]
            data_y = np.array(data[cols[0]]) / np.array(data[cols[1]])

        else:
            col = int(col)
            time.sleep(1)
            data_y = np.array(data[col])

        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        color = colors[cnum]

        # if cnum == 3:
        #     color = colors[4]

        if   STYLE == 'point': ax.scatter(data_x, data_y,      c=color, label=label, s=10)
        elif STYLE == 'line' : ax.plot   (data_x, data_y, 'b', c=color, label=label)
        elif STYLE == 'step' : ax.step   (data_x, data_y, 'b', c=color, label=label)
        elif STYLE == 'bar'  : ax.bar    (data_x, data_y,      c=color, label=label)
        elif STYLE == 'hist' : ax.hist   (data_y,  150,        color=color, label=label)



except IndexError:
    print('index error')
    for i,e in enumerate(data[0]):
        print('    %2d: %s' % (i, e))
    raise

if LEGEND != ['-']:
    plt.legend(ncol=1, fancybox=True)

if TITLE   : ax.set_title(TITLE, loc='center')
if LOG_X   : ax.set_xscale('log')
if LOG_Y   : ax.set_yscale('log')
if LABEL_X : ax.set_xlabel(to_latex(LABEL_X))
if LABEL_Y : ax.set_ylabel(to_latex(LABEL_Y))
if TICKS_X : ax.set_xticks([int(t) for t in TICKS_X], TICKS_X)
if TICKS_Y : ax.set_yticks([int(t) for t in TICKS_Y], TICKS_Y)
if GRID    : ax.grid(True)

xmin, xmax, ymin, ymax = RANGE
if xmin is not None: ax.set_xlim(left=0)
if xmax is not None: ax.set_xlim(right=0)
if ymin is not None: ax.set_ylim(left=0)
if ymax is not None: ax.set_ylim(right=0)

if not FNAME:
    FNAME = TITLE.lower().replace(' ', '_')
    FNAME = FNAME.replace(':', '_-_')
    FNAME = FNAME.replace('__', '_')

if   SAVE_AS == 'png': fig.savefig('%s.png' % FNAME, bbox_inches="tight")
elif SAVE_AS == 'svg': fig.savefig('%s.svg' % FNAME, bbox_inches="tight")
elif SAVE_AS == 'pdf': fig.savefig('%s.pdf' % FNAME, dpi=300,
                                              bbox_inches="tight")
elif SAVE_AS == 'x11': fig.show()


# ------------------------------------------------------------------------------

