#!/usr/bin/env python

"""
This is a wrangler for RADICAL-Pilot (RP) sessions. It assumes the following:

* One RP session corresponds to one experiment run.
* One experiment has multiple runs.
* Profiles and json file have been collected for each RP session.
* Data for each session are collected into a directory with the same name as
  the session ID. For example: 'rp.session.titan-ext1.merzky1.017242.0012'.
* All the session directories are collected into a single experiment directory.
* All the experiment directories are collected within a single data directory.

The wrangler cycles through all the experiment directories within the data
directory and calculates all the durations for each session, pilot, and unit.
Durations and associated timestamps are saved into three csv files:
sessions.csv for the session entities; pilots.csv for pilot entities; and
units.csv for unit entities.

CSV files are written incrementally

Examples:

* Typically, data are organized in a directory trhee similar to:
  data/exp1/rp.session.titan-ext1.merzky1.017242.0012

Todo:

1. Intercept and handle more errors from ra:
  - ValueError: no duration defined for given constraints
2. Eliminate records in units/pilots when session fails to wrangle
   (transactions).

"""

import os
import sys
import glob
import fcntl
import getopt
import psutil
import numpy as np
import pandas as pd
import multiprocessing as mp

import radical.utils     as ru
import radical.pilot     as rp
import radical.analytics as ra

from sqlalchemy import create_engine


# ------------------------------------------------------------------------------
#
def help():
        message = """
        -d --ddir       Name of the directory containing all the experiment
                        directories. For example '../data'.
        -t --etag       Name of the tag identifying each experiment directory.
                        For example, given three experiment directories exp1,
                        exp2, exp3, the experiment tag is 'exp'.
        -e --eid        Number of the experiment to wrangle. For example '1'.
                        When specified, the wrangler wrangles only the
                        sessions wihtin this experiment directory -t+-e (exp1).
        -s --sid        Name of the directory of a session of RADICAL Pilot.
                        For example 'rp.session.radical.mturilli.017233.0002'.
                        When specified, the wrangler wrangles only this
                        session.
        -o --odir       Name of the directory where to load and save the csv
                        files created by the wrangler. When not specified,
                        -d is used.
        -h --help       Prints the help page.
        -u --usage      Prints usage command.
        """
        return usage() + message


# ------------------------------------------------------------------------------
#
def usage():
        message = """
        ra-wrangler.py -d <directory> -t <tag>
                       [-e <integer>] [-s <rp_session_ID>][-o <directory>]
                       [-h] [-u]
        """
        return message


# ------------------------------------------------------------------------------
#
def clparse(argv):
    clopts = {'ddir': None,  # data directory (mandatory).
              'eid' : None,  # experiment tag (mandatory).
              'enum': None,  # experiment number.
              'sid' : None,  # session ID.
              'odir': None}  # directory where to save csv files.

    try:
        opts, args = getopt.getopt(argv, 'hud:t:e:s:o:',
            ['help','usage','ddir=','etag=','eid=','sid=','odir='])
        if not opts:
            print('No options supplied')
            print(usage())
            sys.exit(1)

    except getopt.GetoptError as e:
        print(e)
        usage()
        sys.exit(2)

    for opt, arg in opts:

        if opt in ['-h', '--help']:
            print(help())
            sys.exit(0)

        if   opt in ('-d', '--edir'): clopts['ddir'] = arg
        elif opt in ('-t', '--etag'): clopts['etag'] = arg
        elif opt in ('-e', '--eid') : clopts['eid']  = arg
        elif opt in ('-s', '--sid') : clopts['sid']  = arg
        elif opt in ('-o', '--odir'): clopts['odir'] = arg
        else: raise ValueError('invalid option %s' % opt)


    # Define the directory where to output the cvs files created by the
    # wrangler.
    if not clopts['odir']:
        clopts['odir'] = clopts['ddir']

    # Check for mandatory arguments
    if not clopts['ddir'] or not clopts['etag']:
        print('One or more mandatory option was not supplied')
        print(usage())
        sys.exit(3)

    return clopts


# ------------------------------------------------------------------------------
#
def initialize_entity(etype=None):

    # Columns for each entity's csv
    entities = {
        'session': {'sid'          : [],     # Session ID
                    'session'      : [],     # RA session objects
                    'experiment'   : [],     # Experiment ID
                    'nhost'        : [],     # #host for CU execution
                    'nunit'        : [],     # #units
                    'nunit_done'   : [],     # #active units
                    'nunit_failed' : [],     # #failed units
                    'npilot'       : [],     # #pilots
                    'npilot_active': [],     # #active pilots
                    'ncore'        : [],     # #cores
                    'ncore_active' : []},    # #active cores
        'pilot'  : {'pid'          : [],     # Pilot ID
                    'sid'          : [],     # Session ID
                    'hid'          : [],     # Host ID
                    'ncore'        : [],     # #cores
                    'nunit'        : [],     # #units executed
                    'experiment'   : []},    # Experiment ID
        'unit'   : {'uid'          : [],     # Unit ID
                    'sid'          : [],     # Session ID
                    'pid'          : [],     # Pilot ID
                    'hid'          : [],     # Host ID
                    'experiment'   : []}}    # Experiment ID

    # Add the duration label of each state of each entity.
    for duration in pdm:
        entities['session'][duration] = list()
        entities['pilot'][duration]   = list()

    for duration in udm:
        entities['session'][duration] = list()
        entities['unit'][duration]    = list()

    if etype not in ['session', 'pilot', 'unit']:
        print('Cannot itialize entity %s' % etype)
        sys.exit(1)

    # Return the empty data structure of the requested entity.
    return entities[etype]


# ------------------------------------------------------------------------------
#
def load_df(etype=None, sid=None):

    if etype not in ['session', 'pilot', 'unit']:
        print('Cannot itialize entity %s' % etype)
        sys.exit(1)

    # Initialize an empty DF with the entity's properties.
    df = pd.DataFrame(initialize_entity(etype=etype))

    # Load the entity's csv into a Panda DataFrame.
    if os.path.isfile(csvs[etype]):
        df = pd.read_csv(csvs[etype], index_col=0)

        # Prune the DF to save memory.
        if sid:
            df = df[df.sid == sid]

    return df


# ------------------------------------------------------------------------------
#
def store_df(new_df, stored=pd.DataFrame(), etype=None):

    # skip storing if no new data are passed.
    if new_df.empty:
        print('WARNING: attempting to store an empty DF (skip).')
        return

    # Set header for csv file
    header = True
    if os.path.isfile(csvs[etype]):
        header = False

    if etype == 'session':
        new_sessions = new_df.drop('session', axis=1)
        if stored.empty:
            sessions = new_sessions
        else:
            sessions = stored.append(new_sessions)
        sessions.to_csv(csvs[etype])

    elif etype not in ['pilot', 'unit']:
        print('Cannot store DF to %s' % etype)
        sys.exit(1)

    if stored.empty:
        df = new_df

    else:
        df = stored.append(new_df, ignore_index=True)

    df.reset_index(inplace=True, drop=True)

    with open(csvs[etype], 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        df.to_csv(f, header=header)
        fcntl.flock(f, fcntl.LOCK_UN)


# ------------------------------------------------------------------------------
#
def parse_osg_hostid(hostid):
    '''
    Heuristic: eliminate node-specific information from hostID.
    '''
    domain = None

    # Split domain name from IP.
    host = hostid.split(':')

    # Split domain name into words.
    words = host[0].split('.')

    # Get the words in the domain name that do not contain
    # numbers. Most hostnames have no number but there are
    # exceptions.
    literals = [l for l in words 
                  if not any((number in set('0123456789')) for number in l)]

    # Check for exceptions:
    # a. every word of the domain name has a number
    if len(literals) == 0:

        # Some hostname use '-' instead of '.' as word separator.
        # The parser would have returned a single word and the
        # any of that word may have a number.
        if '-' in host[0]:
            words    = host[0].split('-')
            literals = [l for l in words if not
                        any((number in set('0123456789')) for number in l)]

            # FIXME: We do not check the size of literals.
            domain = '.'.join(literals)

        # Some hostnames may have only the name of the node. We
        # have to keep the IP to decide later on whether two nodes
        # are likely to belong to the same cluster.
        elif 'nod' in host[0]:
            domain = '.'.join(host)

        # FIXME: ad hoc parsing
        elif 'n0' in host[0]:
            domain = 'n0x.10.2.x.x'

        # The hostname is identified by an alphanumeric string
        else:
            domain = '.'.join(host)

    # Some hostnames DO have numbers in their name.
    elif len(literals) == 1:
        domain = '.'.join(words[1:])

    # Some hostname are just simple to parse.
    else:
        domain = '.'.join(literals)

    # FIXME: When everything else fails, ad hoc manipulations of domain string.
    if   'its.osg' in domain: domain = 'its.osg'
    elif 'nodo'    in domain: domain = 'nodo'
    elif 'bu.edu'  in domain: domain = 'bu.edu'

    return domain


# ------------------------------------------------------------------------------
#
def load_pilots(sid, exp, sra_pilots, pdm, pu_rels, pts):

    sys.stdout.write('\n%s --- %s' % (exp, sid))
    ps = initialize_entity(etype='pilot')

    # Did we already store pilots of this session?
    stored_pilots = load_df(etype='pilot', sid=sid)
    stored_pids   = list()

    if stored_pilots['sid'].any():
        stored_pilots_sid = stored_pilots.loc[stored_pilots['sid'] == sid].copy()
        stored_pids       = stored_pilots_sid['pid'].values.tolist()

    # Derive properties and duration for each pilot.
    for pid in sorted(sra_pilots.list('uid')):

        # Skip session if its pilots have been already stored.
        if pid in stored_pids:
            sys.stdout.write('\n%s already in %s' % (pid, csvs['pilot']))
            continue

        # Pilot properties.
        sys.stdout.write('\n' + pid + ':\n')
        ps['pid'].append(pid)
        ps['sid'].append(sid)
        ps['experiment'].append(exp)

        # Get pilot entity from RA session.
        pentity = sra_pilots.get(uid=pid)[0]

        # Host ID.
        if pentity.cfg['hostid']:
            ps['hid'].append(parse_osg_hostid(pentity.cfg['hostid']))
        else:
            ps['hid'].append(np.nan)

        # Number of cores of the pilot.
        ps['ncore'].append(pentity.description['cores'])

        # Number of units executed.
        ps['nunit'].append(len(pu_rels[pid]))

        # Pilot Timestamps.
        for state in pts:
            if state not in ps:
                ps[state] = list()

            try:
                ps[state].append(pentity.timestamps(state=state)[0])
            except:
                if state not in rp.FINAL:
                    print('WARNING: no timestamp for state %s' % state)
                ps[state].append(np.nan)

        # Pilot durations.
        for duration in pdm:

            # TODO: AM: why are not all inserted here?
            #           Can there be more than one (why is it a list)?
            if duration not in ps:
                ps[duration] = list()

            try:
                ps[duration].append(pentity.duration(event=pdm[duration]))
                sys.stdout.write(' %s' % duration)
            except:
                print(' WARNING: Failed to calculate duration %s' % duration)
                ps[duration].append(np.nan)

    # Store pilots DF to csv and reload into memory to return the complete
    # DF for the given sid.
    if ps['pid']:
        pilots = pd.DataFrame(ps)
        # FIXME: This is a workaround to load the full DF before saving it. The
        # DF is then unloaded loading only the portion related to the pilots
        # just wrangled. This avoids using memory but needs cleanup.
        store_df(pilots, etype='pilot')
        stored_pilots = load_df(etype='pilot', sid=sid)
        print('\nstored in %s.' % csvs['pilot'])

    # Returns the DF of the stored pilots if no new pilots have been added;
    # the DF with the old and new pilots otherwise.
    return stored_pilots


# ------------------------------------------------------------------------------
#
def load_units(sid, exp, sra_units, udm, pilots, sra, pu_rels, uts):

    sys.stdout.write('\n%s --- %s' % (exp, sid))
    us = initialize_entity(etype='unit')

    # Did we already store units of this session?
    stored_units = load_df(etype='unit', sid=sid)
    stored_uids  = list()

    if stored_units['sid'].any():
        stored_units_sid = stored_units.loc[stored_units['sid'] == sid].copy()
        stored_uids = stored_units_sid['uid'].values.tolist()

    # Derive properties and duration for each unit.
    for uid in sorted(sra_units.list('uid')):

        # Skip session if its pilots have been already stored.
        if uid in stored_uids:
            sys.stdout.write('\n%s already stored in %s' % (uid, csvs['unit']))
            continue

        # Properties.
        sys.stdout.write('\n' + uid + ':\n')
        us['uid'].append(uid)
        us['sid'].append(sid)
        us['experiment'].append(exp)

        # Get unit entity from RA session
        uentity = sra_units.get(uid=uid)[0]

        # Unit Timestamps.
        for state in uts:
            if state not in us:
                us[state] = list()

            try:
                us[state].append(uentity.timestamps(state=state)[0])
            except:
                if state not in ['CANCELED', 'FAILED']:
                    print('WARNING: Failed to get timestampe for %s' % state)
                us[state].append(np.nan)

        # Durations.
        for duration in udm:
            if duration not in us:
                us[duration] = list()
            try:
                # TODO: this is a temporary fix for inconsistent state model.
                # TODO: AM: WHAT INCONSISTENT STATE MODEL?? ;)  Still needed?
                if duration == 'U_AGENT_EXECUTING':
                    if 'AGENT_STAGING_OUTPUT_PENDING' in uentity.states and \
                       'FAILED'                       in uentity.states:
                        us[duration].append(np.nan)
                        continue

                us[duration].append(uentity.duration(event=udm[duration]))
                sys.stdout.write(' %s' % duration)

            except:
                print('\nWARNING: Failed to calculate duration %s' % \
                    duration)
                us[duration].append(np.nan)

        # pilot and host on which the unit has been executed.
        punit = [key[0] for key in list(pu_rels.items())
                        if  uid in key[1]]
        if punit:
            punit = punit[0]
        else:
            print('\nDEBUG: pu_rels.items():\n' % list(pu_rels.items()))
            print('WARNING: empty pilot name for unit %s' % uid)
            punit = None

        hid = pilots[(pilots['sid'] == sid) &
                     (pilots['pid'] == punit)]['hid'].tolist()[0]
        
        us['pid'].append(punit)
        us['hid'].append(hid)

    # Store unit DF to csv and reload into memory to return the complete
    # DF for the given sid.
    if us['pid']:
        units = pd.DataFrame(us)
        # FIXME: This is a workaround to load the full DF before saving it. The
        # DF is then reloaded, loading only the units just wrangled. This
        # avoids using memory but needs cleanup.
        #
        store_df(units, etype='unit')
        stored_units = load_df(etype='unit', sid=sid)
        print('\nstored in %s.' % csvs['unit'])

    # Returns the DF of the stored pilots if no new pilots have been added;
    # the DF with the old and new pilots otherwise.
    return stored_units


# ------------------------------------------------------------------------------
#
def load_session(sid, exp, sra_session, sra_pilots, sra_units,
                 sdm, pdm, udm, pilots, units, sts):

    # REDUNDANT: get_new_sessions checks for this already
    # If this session has been already stored get out, nothing to do here.
    # stored_sessions = load_df(etype='session', sid=sid)
    # if sid in stored_sessions.index.tolist():
    #     sys.stdout.write('%s already stored in %s' % (sid, csvs['session']))
    #     return False

    sys.stdout.write('\n%s --- %s' % (exp, sid))
    s = initialize_entity(etype='session')

    # Session properties: pilots and units.
    # sp = sra_session.filter(etype='pilot', inplace=False)
    # su = sra_session.filter(etype='unit', inplace=False)
    s['sid'].append(sid)
    s['session'].append(None)
    s['experiment'].append(exp)
    s['nhost'].append(len(pilots.loc[pilots['sid'] == sid]['hid'].unique()))
    s['nunit'].append(len(sra_units.get()))
    s['npilot'].append(len(sra_pilots.get()))
    s['npilot_active'].append(len(sra_pilots.timestamps(state='PMGR_ACTIVE')))
    s['nunit_done'].append(len(sra_units.timestamps(state='DONE')))
    s['nunit_failed'].append(len(sra_units.timestamps(state='FAILED')))

    # Number of cores requested and used by the session's pilots. Make a copy of
    # the pilots DF with only the columns we need to limit memory overhead.
    pcores = pilots[pilots.sid == sid][['P_LRMS_RUNNING', 'ncore']]
    s['ncore'].append(pcores.ncore.sum())
    s['ncore_active'].append(pcores[pcores.P_LRMS_RUNNING > 0].ncore.sum())
    pcores = None

    # Session timestamps.
    # for state in sts:
    #     if state not in s:
    #         s[state] = list()
        # FIXME: Open a ticket requesting timestamps for session's events.
        # s[state].append(min(sra_pilots.timestamps(state=state)))
    s['NEW'] = list()
    s['NEW'].append(min(sra_pilots.timestamps(state='NEW')))

    # Session total duration.
    # for duration in sdm:
    #     if duration not in s:
    #         s[duration] = list()
    #     s['TTC'].append(sra_session.ttc)
    s['TTC'] = list()
    s['TTC'].append(sra_session.ttc)

    # Pilots total durations.  NOTE: s initialization guarantees
    # the existence of duration keys.
    for duration in pdm:
        s[duration].append(sra_pilots.duration(event=pdm[duration]))

    # Units total durations. NOTE: s initialization guarantees the
    # existence of duration keys.
    for duration in udm:
        s[duration].append(sra_units.duration(event=udm[duration]))

    # Store session.
    session = pd.DataFrame(s, index=[sid])
    # FIXME: This is a workaround to load the full DF before saving it.
    stored_sessions = load_df(etype='session')
    store_df(session, stored=stored_sessions, etype='session')
    print('\nstored in %s' % csvs['session'])

    return stored_sessions


# ------------------------------------------------------------------------------
#
def get_raw_sessions(ddir, etag, clopts):
    '''
    Get sessions ID, experiment number and RA object.
    Assume: ddir/exp*/sessiondir/session.json.
    '''

    print('\n\nGet raw sessions: ')
    sids = dict()

    for path in glob.glob('%s/%s*' % (ddir, etag)):

        # Every directory in the experiment dir is assumed to be a RP session.
        for sdir in glob.glob('%s/*/' % path):

            # we assume the dir name is the session ID (after stripping '/'-es)
            sdir = sdir.rstrip('/')
            sid  = os.path.basename(sdir)

            # Skip session if not specified at command line.
            if clopts['sid'] and clopts['sid'] != sid:
                print('Ignore directory %s; waiting for %s' % (sdir,
                    clopts['sid']))
                continue

            # Get session ID directory if json file exists.
            # sid = glob.glob('%s/*.json' % sdir)[0].split('/')[-2]
            if not os.path.isfile('%s/%s.json' % (sdir, sid)):
                print("ERROR: no session json in %s" % sdir)
                print("Skip %s" % sdir)
                continue

            # Get experiment directory.
            exp = os.path.basename(path)

            # Skip session if not in the experiment directory specified at
            # command line.
            # FIXME: AM: I don't understand the index notation below
            if clopts['eid'] and clopts['eid'] != exp[len(etag):]:
                print('Ignore %s; looking for directories in %s' % (
                    exp[len(etag):], clopts['eid']))
                continue

            # all tests passed - we want this session
            sids[sdir] = sid

    print('Done.')
    return sids


# ------------------------------------------------------------------------------
#
def get_new_sessions(sids):
    '''
    For all sid's given, check if any needs wrangling, and return a dict with
    those session IDs.
    '''

    print('\n\nMarking sessions for wrangling: ')
    towrangle = dict()

    # Load current sessions, pilots, units DFs
    sessions = load_df(etype='session')
    pilots   = load_df(etype='pilot')
    units    = load_df(etype='unit')

    # All sessions are new if we have no stored sessions.
    if sessions.empty:
        return sids

    # Add a session to wrangler when the sesison is not in the sessions DF or
    # when any of the session's units or pilots are not in the units or pilots
    # DFs.
    for sdir, sid in sids.items():
        nurequest = sessions[sessions.sid == sid].nunit.tolist()
        nprequest = sessions[sessions.sid == sid].npilot.tolist()

        # Duplicates in sessions need to be addressed manually by the user.
        # TODO: AM: ?
        if (len(nurequest) > 1) or (len(nprequest) > 1):
            print('ERROR: Duplicate entries for sid %s in sessions df' % sid)
            sys.exit(1)

        if  sid not in sessions.sid.tolist()                  or \
            units[units.sid   == sid].shape[0] < nurequest[0] or \
            pilots[pilots.sid == sid].shape[0] < nprequest[0] :
            print('Mark session %s for wrangling' % sid)
            towrangle[sdir] = sid

    print('Done.')
    return towrangle


# ------------------------------------------------------------------------------
#
def wrangle_session(sdir, sid):

    # Get the experiment tag for the current sdir.
    exp = sdir.split('/')[-2:][0]

    # RA objects cannot be serialize: every RA session object need
    # to be constructed at every run.
    #
    # FIXME: AM: Actually, RA sessions can be pickled all right:
    #
    #        import radical.analytics as ra
    #        import pickle
    #        s1 = ra.Session(src=sdir, stype='radical.pilot')
    #        p  = pickle.dumps(s1)
    #        s2 = pickle.loads(p)
    #        assert(len(s1.get()) == len(s2.get()))
    #
    #        If we found cases where this does not work, we can make it work.
    #
    sra_session = ra.Session(sdir, 'radical.pilot')

    # Pilot-unit relationship dictionary
    pu_rels = sra_session.describe('relations', ['pilot', 'unit'])

    # Pilots of sra: dervie properties and durations.
    print('\n\n%s -- %s -- Loading pilots:' % (exp, sid))
    sra_pilots = sra_session.filter(etype='pilot', inplace=False)
    pilots     = load_pilots(sid, exp, sra_pilots, pdm, pu_rels, pts)

    # Units of sra: dervie properties and durations.
    print('\n\n%s -- %s -- Loading units:' % (exp, sid))
    sra_units = sra_session.filter(etype='unit', inplace=False)
    units     = load_units(sid, exp, sra_units, udm, pilots,
                           sra_session, pu_rels, uts)

    # Session of sra: derive properties and total durations.
    print('\n\n%s -- %s -- Loading session:\n' % (exp, sid))
    load_session(sid, exp, sra_session, sra_pilots, sra_units,
                 sdm, pdm, udm, pilots, units, sts)


# =============================================================================
if __name__ == '__main__':

    # Get command line options
    clopts = clparse(sys.argv[1:])

    # Where to find data (ddir) and how data are stored into experiments
    # (etag).
    ddir = clopts['ddir']  # e.g., '../data/'
    etag = clopts['etag']  # e.g., 'exp'

    # File names where to save the DF of each entity of each session.
    csvs = {'session': '%s/sessions.csv' % clopts['odir'],
            'pilot'  : '%s/pilots.csv'   % clopts['odir'],
            'unit'   : '%s/units.csv'    % clopts['odir']}

    # FIXME: Define timestamps of the events of the pilot's states.
    sts = {rp.NEW     : None,
           rp.DONE    : None,
           rp.CANCELED: None,
           rp.FAILED  : None}

    # FIXME: Define session durations.
    sdm = {'TTC': None}

    # Define timestamps of the events of the pilot's states.
    pts = {rp.NEW                   : None,
           rp.PMGR_LAUNCHING_PENDING: None,
           rp.PMGR_LAUNCHING        : None,
           rp.PMGR_ACTIVE_PENDING   : None,
           rp.PMGR_ACTIVE           : None,
           rp.DONE                  : None,
           rp.CANCELED              : None,
           rp.FAILED                : None}

    # Define pilot durations.
    pdm = {'P_PMGR_SCHEDULING': [{ru.EVENT: 'state',             ru.STATE: rp.NEW                   },
                                 {ru.EVENT: 'state',             ru.STATE: rp.PMGR_LAUNCHING_PENDING}],
           'P_PMGR_QUEUING'   : [{ru.EVENT: 'state',             ru.STATE: rp.PMGR_LAUNCHING_PENDING},
                                 {ru.EVENT: 'state',             ru.STATE: rp.PMGR_LAUNCHING        }],
           'P_LRMS_SUBMITTING': [{ru.EVENT: 'state',             ru.STATE: rp.PMGR_LAUNCHING        },
                                 {ru.EVENT: 'state',             ru.STATE: rp.PMGR_ACTIVE_PENDING   }],
           'P_LRMS_QUEUING'   : [{ru.EVENT: 'state',             ru.STATE: rp.PMGR_ACTIVE_PENDING   },
                                 {ru.EVENT: 'state',             ru.STATE: rp.PMGR_ACTIVE           }],
           'P_LRMS_RUNNING'   : [{ru.EVENT: 'state',             ru.STATE: rp.PMGR_ACTIVE           },
                                [{ru.EVENT: 'state',             ru.STATE: rp.DONE                  },
                                 {ru.EVENT: 'state',             ru.STATE: rp.FAILED                },
                                 {ru.EVENT: 'state',             ru.STATE: rp.CANCELED              }]],

           # from utilization script
           'util_p_total'     : [{ru.EVENT: 'bootstrap_1_start', ru.STATE: None                     },
                                 {ru.EVENT: 'bootstrap_1_stop',  ru.STATE: None                     }],
           'util_p_boot'      : [{ru.EVENT: 'bootstrap_1_start', ru.STATE: None                     },
                                 {ru.EVENT: 'sync_rel',          ru.STATE: None                     }],
           'util_p_setup_1'   : [{ru.EVENT: 'sync_rel',          ru.STATE: None                     },
                                 {ru.EVENT: 'orte_dvm_start',    ru.STATE: None                     }],
           'util_p_orte'      : [{ru.EVENT: 'orte_dvm_start',    ru.STATE: None                     },
                                 {ru.EVENT: 'orte_dvm_ok',       ru.STATE: None                     }],
           'util_p_setup_2'   : [{ru.EVENT: 'orte_dvm_ok',       ru.STATE: None                     },
                                 {ru.EVENT: 'state',             ru.STATE: rp.PMGR_ACTIVE           }],
           'util_p_uexec'     : [{ru.EVENT: 'state',             ru.STATE: rp.PMGR_ACTIVE           },
                                 {ru.EVENT: 'cmd',               ru.STATE: None                     }],
           'util_p_term'      : [{ru.EVENT: 'cmd',               ru.STATE: None                     },
                                 {ru.EVENT: 'bootstrap_1_stop',  ru.STATE: None                     }],
          }

    # Define timestamps of the events of the pilot's states.
    uts = {rp.NEW                         : None,
           rp.UMGR_SCHEDULING_PENDING     : None,
           rp.UMGR_SCHEDULING             : None,
           rp.UMGR_STAGING_INPUT_PENDING  : None,
           rp.UMGR_STAGING_INPUT          : None,
           rp.AGENT_STAGING_INPUT_PENDING : None,
           rp.AGENT_STAGING_INPUT         : None,
           rp.AGENT_SCHEDULING_PENDING    : None,
           rp.AGENT_SCHEDULING            : None,
           rp.AGENT_EXECUTING_PENDING     : None,
           rp.AGENT_EXECUTING             : None,
           rp.AGENT_STAGING_OUTPUT_PENDING: None,
           rp.AGENT_STAGING_OUTPUT        : None,
           rp.UMGR_STAGING_OUTPUT_PENDING : None,
           rp.UMGR_STAGING_OUTPUT         : None,
           rp.DONE                        : None,
           rp.CANCELED                    : None,
           rp.FAILED                      : None}

    # Define unit durations.
    udm = {'U_UMGR_SCHEDULING'      : [{ru.EVENT: 'state',                  ru.STATE: rp.NEW                         },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.UMGR_SCHEDULING_PENDING     }],
           'U_UMGR_BINDING'         : [{ru.EVENT: 'state',                  ru.STATE: rp.UMGR_SCHEDULING_PENDING     },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.UMGR_SCHEDULING             }],
         # 'I_UMGR_SCHEDULING'      : [{ru.EVENT: 'state',                  ru.STATE: rp.UMGR_SCHEDULING             },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_INPUT_PENDING  }],
         # 'I_UMGR_QUEING'          : [{ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_INPUT_PENDING  },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_INPUT          }],
         # 'I_AGENT_SCHEDULING'     : [{ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_INPUT          },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_INPUT_PENDING }],
         # 'I_AGENT_QUEUING'        : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_INPUT_PENDING },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_INPUT         }],
         # 'I_AGENT_TRANSFERRING'   : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_INPUT         },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_SCHEDULING_PENDING    }],
           'U_AGENT_QUEUING'        : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_SCHEDULING_PENDING    },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_SCHEDULING            }],
           'U_AGENT_SCHEDULING'     : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_SCHEDULING            },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_EXECUTING_PENDING     }],
           'U_AGENT_QUEUING_EXEC'   : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_EXECUTING_PENDING     },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_EXECUTING             }],
           'U_AGENT_EXECUTING'      : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_EXECUTING             },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_OUTPUT_PENDING}],
         # 'O_AGENT_QUEUING'        : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_OUTPUT_PENDING},
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_OUTPUT        }],
         # 'O_UMGR_SCHEDULING'      : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_STAGING_OUTPUT        },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_OUTPUT_PENDING }],
         # 'O_UMGR_QUEUING'         : [{ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_OUTPUT_PENDING },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_OUTPUT         }],
         # 'O_UMGR_TRANSFERRING'    : [{ru.EVENT: 'state',                  ru.STATE: rp.UMGR_STAGING_OUTPUT         },
         #                            [{ru.EVENT: 'state',                  ru.STATE: rp.DONE                        },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.FAILED                      },
         #                             {ru.EVENT: 'state',                  ru.STATE: rp.CANCELED                    }]],

           # from utilization script
            'util_u_total'          : [{ru.EVENT: 'schedule_ok',            ru.STATE: None                           },
                                       {ru.EVENT: 'unschedule_stop',        ru.STATE: None                           }],
            'cu_exec_start_stop'    : [{ru.EVENT: 'cu_exec_start',          ru.STATE: None                           },
                                       {ru.EVENT: 'cu_exec_stop',           ru.STATE: None                           }],
            'util_u_equeue'         : [{ru.EVENT: 'schedule_ok',            ru.STATE: None                           },
                                       {ru.EVENT: 'state',                  ru.STATE: rp.AGENT_EXECUTING             }],
            'util_u_pre_exec'       : [{ru.EVENT: 'cu_pre_start',           ru.STATE: None                           },
                                       {ru.EVENT: 'cu_pre_stop',            ru.STATE: None                           }],
            'util_u_eprep'          : [{ru.EVENT: 'state',                  ru.STATE: rp.AGENT_EXECUTING             },
                                       {ru.EVENT: 'exec_start',             ru.STATE: None                           }],
            'util_u_exec_rp'        : [{ru.EVENT: 'exec_start',             ru.STATE: None                           },
                                       {ru.EVENT: 'cu_start',               ru.STATE: None                           }],
            'util_u_exec_cu'        : [{ru.EVENT: 'cu_start',               ru.STATE: None                           },
                                       {ru.EVENT: 'cu_exec_start',          ru.STATE: None                           }],
            'util_u_exec_orte'      : [{ru.EVENT: 'cu_exec_start',          ru.STATE: None                           },
                                       {ru.EVENT: 'app_start',              ru.STATE: None                           }],
            'util_u_exec_app'       : [{ru.EVENT: 'app_start',              ru.STATE: None                           },
                                       {ru.EVENT: 'app_stop',               ru.STATE: None                           }],
            'util_u_unschedule'     : [{ru.EVENT: 'app_stop',               ru.STATE: None                           },
                                       {ru.EVENT: 'unschedule_stop',        ru.STATE: None                           }],
          }


    # Find out what sessions need to be wrangled.
    rawsids = get_raw_sessions(ddir, etag, clopts)
    sids    = get_new_sessions(rawsids)
    procs   = list()

    print(sids) 

    num_workers = psutil.cpu_count(logical=False)
    workers     = mp.Pool(num_workers)

    # Wrangle the new sessions.
    if sids:
        for sdir,sid in sids.items():
            wrangle_session(sdir, sid)
        #     workers.apply_async(wrangle_session, (sdir, sid,))
        # workers.close()
        # workers.join()

    else:
        print('No new sessions to wrangle found.')

# ------------------------------------------------------------------------------

