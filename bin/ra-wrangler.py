#!/usr/bin/env python3

"""
This is a wrangler for RADICAL Cybertools sessions. It assumes the following:

* One session corresponds to one run of an experiment.
* One experiment has multiple runs and therefore multiple sessions.
* Profiles and json files have been collected for each session.

Sessions are processed in accordance to a given set of durations for a
specific entity of RP (e.g., session, pilot, cu, masters, workers, requests,
stages, pipelines, etc.). The values of each duration is saved into a csv
file. CSV files are written incrementally and sessions that have been already
processed are skipped.

Wrangler can be extended by adding durations and properties extracted from
each session. Both durations and properties are defined in a config file
passed to the wrangler.

Warnings are printed when an expected duration cannot be computed and saved.
"""

import os
import sys
import csv
import json
import argparse

import radical.utils as ru
import radical.analytics as ra
import radical.pilot.states as rps


# ------------------------------------------------------------------------------
def clparse():

    parser = argparse.ArgumentParser(
        description='wrangles RADICAL Cybertools sessions.')

    parser.add_argument('-e', '--entity',
        required=True,
        dest='entity',
        help='type of entity for which to measure durations.')

    parser.add_argument('-m', '--metrics',
        #type=argparse.FileType('r'),
        required=True,    #TODO: make this optional
        dest='metrics',
        help='json file containing the durations.')

    parser.add_argument('-f', '--fout',
        #type=argparse.FileType('a'),
        dest='fout',
        required=True,
        help='csv output file where to write durations.')

    parser.add_argument('sids',
        type=str,
        nargs='+',
        help='list of session IDs.')

    return parser.parse_args()


# -----------------------------------------------------------------------------
def prune_sids(sids, fout):
    pruned = []
    stored = []

    # get the session names already wrangled
    with open(fout, 'rt') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)    # skip headers
        for raw in reader:
            stored.append(raw[0])

    # get the sessions that need to be wrangled.

    # NOTE: `sids` is a list of paths while `stored` is a list of session IDs.
    # We compare the tail of `sids` paths, i.e., the session IDs.
    pruned = [item for item in sids if os.path.split(item)[1] not in stored]

    return pruned


# -----------------------------------------------------------------------------
def get_durations(session, entity, metrics, rels):

    measures = {}

    with open(metrics) as jm:
        durations = json.load(jm)

    # TODO: durations is invalid as json cannot have integers/python objects so
    #       it cannot represent events at the moment. I guess we use non
    #       standard json via RU? Why not using python dictionaries then?
    durations = {'total'     : [{ru.EVENT: 'bootstrap_0_start'},
                                {ru.EVENT: 'bootstrap_0_stop' }],
                 'boot'      : [{ru.EVENT: 'bootstrap_0_start'},
                                {ru.EVENT: 'sync_rel'         }],
                 'setup_1'   : [{ru.EVENT: 'sync_rel'         },
                                {ru.STATE: rps.PMGR_ACTIVE    }],
                 'ignore'    : [{ru.STATE: rps.PMGR_ACTIVE    },
                                {ru.EVENT: 'cmd'              ,
                                 ru.MSG  : 'cancel_pilot'     }],
                 'term'      : [{ru.EVENT: 'cmd'              ,
                                 ru.MSG  : 'cancel_pilot'     },
                                {ru.EVENT: 'bootstrap_0_stop' }]}

    for eid in sorted(session.list('uid')):

        sentity = session.get(uid=eid)[0]

        measures['sid'] = session._sid

        # properties of the entity
        if entity == 'pilot':
            measures['pid'] = eid
            measures['ncores'] = sentity.description['cores']
            measures['ngpus'] = sentity.description['gpus']
            measures['nunits'] = len(rels[eid])

        if entity == 'unit':
            measures['uid'] = eid
            measures['ncores'] = sentity.description['cpu_processes']
            measures['ngpus'] = sentity.description['gpu_processes']
            for pilot, units in rels.items():
                if eid in units:
                    measures['pid'] = pilot

        # durations of the entity
        for duration, events in durations.items():
            try:
                measures[duration] = session.duration(event=events)
            except:
                print('WARNING: Failed to calculate duration %s' % duration)
                measures[duration] = ''

    return measures


# -----------------------------------------------------------------------------
def update_csv(metrics, sid, csv_fname):
    return True


# =============================================================================
if __name__ == '__main__':

    # Get command line options and session IDs
    args = clparse()
    print(args)

    # Find out what sessions need to be wrangled.
    nsids = prune_sids(args.sids, args.fout)
    print(nsids)

    # Wrangle the new sessions, if any.
    if nsids:

        # TODO: we use durations from a given file or the default one in
        # RADICAL pilot (maybe to be moved to RU) for the entities are asked to
        # process.
        if not args.metrics:
            pass

        for sid in nsids:

            # Construct the RADICAL Analytics session object.
            # NOTE: this object can be very large in RAM.
            # TODO: we assume a `radical.pilot` session, we should use
            #       `radical`.
            session = ra.Session(sid, 'radical.pilot')

            # We load entity relationships before unloading entities from the
            # session.
            pu_rels = session.describe('relations', ['pilot', 'unit'])

            # We unload everything but the entities we care about.
            session = session.filter(etype=args.entity, inplace=True)

            # get durations and properties from `session`
            durations = get_durations(session, args.entity, args.metrics,
                pu_rels)
            print(durations)
            sys.exit(0)

            # write session durations and properties to the csv file.
            update_csv(sid, durations, properties, args.fout)

    else:
        print('No new sessions to wrangle found.')
