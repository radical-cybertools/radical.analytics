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
import re
import sys
import csv
import json
import argparse

import radical.analytics as ra


# ------------------------------------------------------------------------------
def clparse():

    parser = argparse.ArgumentParser(
        description='wrangles RADICAL Cybertools sessions.')

    parser.add_argument('-t', '--type_session',
        dest='stype',
        help='type of session: e.g., radical.pilot or radical.entk.')

    parser.add_argument('-e', '--entity',
        required=True,
        dest='entity',
        help='type of entity for which to measure durations.')

    parser.add_argument('-m', '--metrics',
        dest='fmetrics',
        help='json file containing the durations.')

    parser.add_argument('-f', '--fout',
        dest='fout',
        required=True,
        help='csv output file where to write durations.')

    parser.add_argument('sids',
        type=str,
        nargs='+',
        help='list of session IDs.')

    return parser.parse_args()


# -----------------------------------------------------------------------------
def prune_sids(sids, fcsv):

    # no pruning if the csv file does not exist
    if not os.path.isfile(fcsv) or os.stat(fcsv).st_size == 0:
        return sids

    pruned = []
    stored = []

    # get the session names already wrangled
    with open(fcsv, 'rt') as f:
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
def prune_metrics(metrics):

    # RADICAL-Pilot durations have an extra level of tagging that we need to
    # remove to get the dict of default durations.
    # NOTE: should we remove them has they are categories of durations while
    # the dicts are supposed to contain durations?
    pruned = {}

    for tag, duration in metrics.items():
        pruned.update(duration)

    return pruned


# -----------------------------------------------------------------------------
def get_metrics(stype, entity):

    if stype == 'radical.pilot':
        import radical.pilot as rp

        if entity == 'pilot':
            metrics = prune_metrics(rp.utils.PILOT_DURATIONS)
        elif entity == 'unit':
            metrics = prune_metrics(rp.utils.UNIT_DURATIONS_DEFAULT)
        elif entity == 'unit.prrte':
            metrics = prune_metrics(rp.utils.UNIT_DURATIONS_PRTE)
        else:
            raise Exception('ERROR: unknown entity: %s' % entity)

    elif stype == 'radical.entk':

        if entity in ['pipeline', 'stage', 'task']:
            raise Exception('ERROR: RADICAL-EnTK wrangler not implemented.')
        else:
            raise Exception('ERROR: Unknown RADICAL-EnTK entity: %s' % entity)

    else:

        raise Exception('ERROR: Unknown type of session: %s' % stype)

    return metrics


# -----------------------------------------------------------------------------
def convert_metrics(fmetrics):

    metrics = {}

    with open(fmetrics) as jm:
        jmetrics = json.load(jm)

    for name, duration in jmetrics.items():
        metrics[name] = []
        for i, event in enumerate(duration):
            metrics[name].append({})
            for k, v in event.items():
                metrics[name][i].update({int(k): v})

    return metrics


# -----------------------------------------------------------------------------
def measure_entity(sid, sentity, eid, metrics, rels):

    measures = {'sid': sid}

    # properties of the entity
    if entity == 'pilot':
        measures.update({
            'eid'       : eid,
            'resoure'   : sentity.description['resource'],
            'cores'     : sentity.description['cores'],
            'gpus'      : sentity.description['gpus'],
            'project'   : sentity.description['project'],
            'agent_lm'  : sentity.cfg['agent_launch_method'],
            'mpi_lm'    : sentity.cfg['mpi_launch_method'],
            'task_lm'   : sentity.cfg['task_launch_method'],
            'rm'        : sentity.cfg['resource_manager'],
            'dburl'     : sentity.cfg['dburl'],
            'scheduler' : sentity.cfg['scheduler'],
            'spawner'   : sentity.cfg['spawner'],
            'sbox'      : sentity.cfg['session_sandbox'],
            'gpus_node' : sentity.cfg['gpus_per_node'],
           #'cores_node': sentity.cfg['cores_per_node']    TODO: broken,
            'cores_node': sentity.cfg['resource_details']['rm_info']['cores_per_node'],
            'nodes'     : len(sentity.cfg['resource_details']['rm_info']['node_list']),
            'units'     : len(rels[eid])
        })


    if entity == 'unit':
        measures.update({
            'eid'   : eid,
            'ncores': (sentity.description['cpu_processes'] *
                       sentity.description['cpu_threads']),
            'ngpus' : sentity.description['gpu_processes'],
            'did'   : sentity.cfg['pilot']})

    # durations of the entity
    for duration, events in metrics.items():
        try:
            measures[duration] = sentity.duration(event=events)
        except:
            print('WARNING: Failed to calculate %s for %s' % (duration, eid))
            measures[duration] = ''

    return measures


# -----------------------------------------------------------------------------
def measure_global(s, metrics, rels):

    measures = {'sid': s.uid}

    # global properties
    measures.update({
        'n_cores'        : sum([p.description['cores'] for p in s.get(etype='pilot')]),
        'n_gpus'         : sum([p.description['gpus'] for p in s.get(etype='pilot')]),
        # npilot = len(s.filter(etype='pilot').list('uid'))    # Slow+RAM
        'n_pilots'       : len([p for p in s.describe()['tree'].keys() if 'pilot' in p]),
        'n_units'        : len([u for u in s.describe()['tree'].keys() if 'unit' in u]),
        'n_active_pilots': len([p for p in s.get(etype='pilot') if 'PMGR_ACTIVE' in p.states.keys()]),
        'n_failed_pilots': len([p for p in s.get(etype='pilot') if 'FAILED' in p.states.keys()]),
        'n_done_units'   : len([u for u in s.get(etype='unit')  if 'DONE' in u.states.keys()]),
        'n_failed_units' : len([u for u in s.get(etype='unit')  if 'FAILED' in u.states.keys()]),
        'n_nodes'        : sum([len(p.cfg['resource_details']['rm_info']['node_list']) for p in s.get(etype='pilot')])
    })

    #  global durations
        # durations of the entity
    for duration, events in metrics.items():
        try:
            measures[duration] = s.duration(event=events)
        except:
            print('WARNING: Failed to calculate %s' % duration)
            measures[duration] = ''

    return measures

# -----------------------------------------------------------------------------
def is_empty(fcsv):
    content = open(fcsv, 'r').read()
    if re.search(r'^\s*$', content):
        return True


# -----------------------------------------------------------------------------
def update_csv(measures, fcsv):

    # The first time we create the csv file we do not have the headers for
    # that entity. The file can exist but being empty.
    if not os.path.isfile(fcsv) or is_empty(fcsv):
        headers = measures.keys()
        with open(fcsv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerow(measures)

    # write the raw, fill missing headers with '' (restval). If measures has
    # keys not found in the headers, an exception is raised by default.
    else:
        with open(fcsv, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            headers = next(reader, None)

        with open(fcsv, 'a+') as f:
            writer = csv.DictWriter(f, fieldnames=headers, restval='')
            writer.writerow(measures)

    return True


# =============================================================================
if __name__ == '__main__':

    # Get command line options and session IDs
    args     = clparse()
    stype    = args.stype
    entity   = args.entity
    fmetrics = args.fmetrics
    fout     = args.fout
    sids     = args.sids

    # Find out what sessions need to be wrangled.
    sids = prune_sids(sids, fout)
    # print(nsids)

    # Exit if no sessions to wrangle
    if not sids:
        raise Exception('No new sessions to wrangle found.')

    # Exit if entity is unknow
    if entity not in ['session', 'pilot', 'unit']:
        raise Exception('ERROR: Unknown entity %s' % entity)

    # radical.pilot is the default session type
    if not stype:
        stype = 'radical.pilot'

    # We use durations from a given file or the default ones in RADICAL-pilot
    # or RADICAL-EnTK.
    # TODO: implement EnTK metrics in entk.utils.
    if not fmetrics:
        metrics = get_metrics(stype, entity)
        # print('DEBUG: default metrics: %s' % metrics)
    else:
        metrics = convert_metrics(fmetrics)
        # print('DEBUG: json metrics: %s' % metrics)

    for sid in sids:

        # Construct the RADICAL Analytics session object.
        # NOTE: this object can be very large in RAM.
        session = ra.Session(sid, 'radical.pilot')
        pu_rels = session.describe('relations', ['pilot', 'unit'])

        # when entity is session, we get global properties and total durations
        # for thw whole session.
        if entity == 'session':
            measures = measure_global(session, metrics, pu_rels)
            update_csv(measures, fout)

        else:
            # We unload everything but the entities we care about to free RAM.
            session = session.filter(etype=entity, inplace=True)

            # each entity's durations are written as a raw in the csv file.
            # This avoids collecting too may raws into RAM.
            for eid in sorted(session.list('uid')):
                sentity = session.get(etype=entity, uid=eid)[0]
                measures = measure_entity(session.uid, sentity, eid, metrics, pu_rels)
                update_csv(measures, fout)
