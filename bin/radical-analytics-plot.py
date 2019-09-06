#!/usr/bin/env python

import sys
import pprint
import optparse

import numpy             as np
import matplotlib.pyplot as plt

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 14}

plt.rcParams['axes.titlesize']   = 14
plt.rcParams['axes.labelsize']   = 14
plt.rcParams['axes.linewidth']   =  2
plt.rcParams['lines.linewidth']  =  2
plt.rcParams['lines.color']  =  'r'
plt.rcParams['lines.markersize'] = 14
plt.rcParams['xtick.labelsize']  = 14
plt.rcParams['ytick.labelsize']  = 14
plt.rc('font', **font)

# ------------------------------------------------------------------------------
#
TITLE     = None  # 'quick_plot'
DELIM     = ''
COLUMN_X  =  0
COLUMNS_Y = [1]
LEGEND    = []
LABEL_X   = None
LABEL_Y   = None
TICKS_X   = []
TICKS_Y   = []
LOG_X     = False
LOG_Y     = False
SIZE      = (20, 14)
STYLE     = 'line'  # 'point', 'line'
GRID      = True    # True, False
SAVE_AS   = 'x11'   # 'svg', 'png', 'x11'


# ------------------------------------------------------------------------------
#
def usage(parser, msg=None):

    ret = 0
    if msg:
        print '\n\n\t\tError: %s\n' % msg
        ret = 1

    print '''

    usage  : quick_plot.py [<src>] [options]
    example: quick_plot.py experiment.dat -t 'title' --log 'x,y'
    source : space separated datatable (read from stdin if not specified)
    options:
        -h, --help                             : this message
        -t, --title      <title>               : plot title
        -X, --x-label    <label>               : x-axis label
        -Y, --y-label    <label>               : y-axis label
        -d, --delim      <char>                : column delimiter
        -x, --x-column   <col>                 : source column for x-values
        -y, --y-columns  <col_1,col_2,...>     : list of columns columns to plot
        -L, --legend     <label_1,label_2,...> : name of plots specified in '-y'
        -u, --x-ticks    <tick_1,tick_2,...>   : not yet supported
        -v, --y-ticks    <tick_1,tick_2,...>   : not yet supported
        -s, --style      <points | line>       : line style
        -z, --size       <20,14>               : canvas size
        -l, --log        <x | y | x,y>         : log-scale for x and/or y axis
        -a, --save-as    <png | svg | x11>     : save fig in format (x11: show)

'''

    sys.exit(ret)


# ------------------------------------------------------------------------------
# parse options
parser = optparse.OptionParser(add_help_option=False)

parser.add_option('-t', '--title',     dest='title')
parser.add_option('-X', '--x-label',   dest='xlabel')
parser.add_option('-Y', '--y-label',   dest='ylabel')
parser.add_option('-d', '--delimiter', dest='delim')
parser.add_option('-x', '--x-column',  dest='xcol')
parser.add_option('-y', '--y-columns', dest='ycols')
parser.add_option('-u', '--x-ticks',   dest='xticks')
parser.add_option('-v', '--y-ticks',   dest='yticks')
parser.add_option('-L', '--legend',    dest='legend')
parser.add_option('-s', '--style',     dest='style')
parser.add_option('-z', '--size',      dest='size')
parser.add_option('-l', '--log',       dest='log')
parser.add_option('-a', '--save-as',   dest='save')
parser.add_option('-h', '--help',      dest='help', action="store_true")

options, args = parser.parse_args()
if len(args) > 1:
    usage(parser, "Too many arguments (%s)" % args)

if len(args) < 1:
    src = None
else:
    src = args[0]

if options.help   : usage(parser)
if options.title  : TITLE        =  str (options.title)
if options.delim  : DELIM        =  str (options.delim)
if options.xcol   : COLUMN_X     =  int (options.xcol)
if options.ycols  : COLUMNS_Y    = [int (x) for x in options.ycols .split(',')]
if options.xlabel : LABEL_X      =  str (options.xlabel)
if options.ylabel : LABEL_Y      =  str (options.ylabel)
if options.xticks : TICKS_X      = [str (x) for x in options.xticks.split(',')]
if options.yticks : TICKS_Y      = [str (x) for x in options.yticks.split(',')]
if options.legend : LEGEND       = [str (x) for x in options.legend.split(',')]
if options.log    : LOG_X, LOG_Y = [bool(int(x)) for x in options.log   .split(',')]
if options.style  : STYLE        =  str (options.style)
if options.size   : SIZE         = [int (x) for x in options.size  .split(',')]
if options.save   : SAVE_AS      =  str (options.save)


if SAVE_AS not in ['x11', 'png', 'svg']:
    raise ValueError('invalid save_as value: %s' % SAVE_AS)

if STYLE not in ['point', 'line', 'step']:
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


def get_elems(line):
    if DELIM:
        elems = [e.strip() for e in line.split(DELIM)]
        print elems
    else:
        elems = line.split()

    ret = list()
    for e in elems:
        try:
            ret.append(float(e))
        except:
            ret.append(e)

    return ret


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
        rows.append(get_elems(line))

# ------------------------------------------------------------------------------
# invert rows to actual data layout
data  = list()
ncols = len(rows[0])
for idx in range(ncols):
    data.append(list())

for row in rows:
    for col in range(ncols):
        data[col].append(row[col])

# ------------------------------------------------------------------------------
# plot data
plt.figure(figsize=SIZE)
# pprint.pprint(data)
try:
    cnum = 0
    for col in COLUMNS_Y:

        if LEGEND: label = LEGEND[cnum]
        else     : label = str(cnum)
        cnum += 1

        data_x = np.array(data[COLUMN_X])
        data_y = np.array(data[col])

        if   STYLE == 'point': plt.scatter(data_x, data_y, label=label, s=10)
        elif STYLE == 'line' : plt.plot   (data_x, data_y, 'b', label=label)
        elif STYLE == 'step' : plt.step   (data_x, data_y, 'b', label=label)

except IndexError:
    print 'index error'
    for i,e in enumerate(data[0]):
        print '    %2d: %s' % (i, e)
    raise

plt.legend(ncol=2, fancybox=True, loc='lower right')

# if TITLE   : plt.title(TITLE)
if LOG_X   : plt.xscale('log')
if LOG_Y   : plt.yscale('log')
if LABEL_X : plt.xlabel(LABEL_X)
if LABEL_Y : plt.ylabel(LABEL_Y)
if TICKS_X : plt.xticks([int(t) for t in TICKS_X], TICKS_X)
if TICKS_Y : plt.yticks([int(t) for t in TICKS_Y], TICKS_Y)
if GRID    : plt.grid(True)

fbase = TITLE.lower()
if   SAVE_AS == 'png': plt.savefig('%s.png' % (TITLE.lower()), bbox_inches="tight")
elif SAVE_AS == 'svg': plt.savefig('%s.svg' % (TITLE.lower()), bbox_inches="tight")
elif SAVE_AS == 'x11': plt.show()


# ------------------------------------------------------------------------------

