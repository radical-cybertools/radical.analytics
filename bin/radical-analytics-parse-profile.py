#!/usr/bin/env python3

import sys
import time
import optparse                              # pylint: disable=deprecated-module

from collections import defaultdict

import radical.utils as ru


# ------------------------------------------------------------------------------
#
def usage(msg=None):

    ret = 0
    if msg:
        print('\n\n\t\tError: %s\n' % msg)
        ret = 1

    print('''

    usage  : radical-analytics-parse-profile [options] [<src>]
    example: radical-analytics-parse-profile -s 'start' -e 'start,stop' sample.prof
    source : profiler as written by `ru.Profiler`
    options:
        -h, --help                             : this message
        -n, --normalize                        : normalize timestamps
        -s, --sort-by    <event>               : sort resulting data by `event`
        -e, --events     <event_1,event_2,...> : event timestamps to extract
        -o, --output     <filename>            : output filename

    The profile will parsed for the given set of events, and the resulting data
    will be written to the given output file in the following format:


       <uid> <timestamp_1> <timestamp_2> ...

    where the timestamps correspond to the respective events.  The table will be
    sorted by the event given with `--sort-by`, if given.  If no `--sort-by` is
    given, the table will be sorted by the first timestamp column.  If
    `--normalize` is given, all timestamps will be normalized to the timestamp
    of the first event.

''')

    sys.exit(ret)


# ------------------------------------------------------------------------------
#
# parse options
#
parser = optparse.OptionParser(add_help_option=False)

parser.add_option('-h', '--help',      dest='help',      action='store_true')
parser.add_option('-n', '--normalize', dest='normalize', action='store_true')
parser.add_option('-s', '--sort-by',   dest='sort_by')
parser.add_option('-e', '--events',    dest='events')
parser.add_option('-o', '--output',    dest='output')

options, args = parser.parse_args()
if len(args) > 1:
    usage("Too many arguments (%s)" % args)

if len(args) < 1:
    src = None
else:
    src = args[0]

EVENTS = None
OUTPUT = None

if options.help  : usage()
if options.events: EVENTS = [x for x in options.events.split(',')]
if options.output: OUTPUT = options.output

data = defaultdict(dict)
tmin = None

tmin = time.time()  # assume that profiles were collected in the past

try:
    fin = None
    if src is None:
        fin = sys.stdin
    else:
        fin = ru.ru_open(src, 'r')

    for line in fin.readlines():
        elems = line.split(',')
        if EVENTS and elems[1] not in EVENTS:
            continue
        time  = float(elems[0])
        tmin  = min(tmin, time)
        uid   = elems[4]
        event = elems[1]
        data[uid][event] = time

finally:
    if fin: fin.close()


if not EVENTS:
    EVENTS = list(data[list(data.keys())[0]].keys())


if options.normalize:
    for uid in data:
        for event in data[uid]:
            data[uid][event] = data[uid][event] - tmin

try:
    if not OUTPUT:
        fout = sys.stdout
    else:
        fout = ru.ru_open(OUTPUT, 'w')

    fout.write('# %13s ' % 'uid')
    for event in EVENTS:
        fout.write('%17s ' % event)
    fout.write('\n')

    uids = list(data.keys())
    if options.sort_by:
        uids = sorted(uids, key=lambda uid: data[uid].get(options.sort_by, 0.0))

    for uid in uids:
        out = '%15s ' % uid
        for event in EVENTS:
            val = data[uid].get(event, 0.0)
            out += '%10.6f ' % val
        fout.write('%s\n' % out)

finally:
    if fout: fout.close()

