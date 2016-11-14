#!/usr/bin/env python
"""This script does x.

Example:

Attributes:

Todo:

"""

import os
import sys
import glob
import numpy as np
import pandas as pd
import radical.analytics as ra


def initialize_entity(ename=None):
    entities = {'session': {'session'      : [],   # RA session objects
                            'experiment'   : [],   # Experiment ID
                            'TTC'          : [],   # Time to completion
                            'nhost'        : [],   # #host for CU execution
                            'nunit'        : [],   # #units
                            'npilot'       : [],   # #pilots
                            'npilot_active': []},  # Number of active pilots
                'pilot'  : {'pid'          : [],   # Pilot ID
                            'sid'          : [],   # Session ID
                            'hid'          : [],   # Host ID
                            'experiment'   : []},  # Experiment ID
                'unit'   : {'uid'          : [],   # Unit ID
                            'sid'          : [],   # Session ID
                            'hid'          : [],   # Host ID
                            'experiment'   : []}}  # Experiment ID

    # Add the duration label of each state of each entity.
    for duration in pdm.keys():
        entities['session'][duration] = []
        entities['pilot'][duration] = []
    for duration in udm.keys():
        entities['session'][duration] = []
        entities['unit'][duration] = []

    # Return the empty data structure of the requested entity.
    if ename in ['session', 'pilot', 'unit']:
        return entities[ename]
    else:
        error = 'Cannot itialize entity %s' % ename
        print error
        sys.exit(1)


def load_df(ename=None):
    if ename in ['session', 'pilot', 'unit']:
        df = pd.DataFrame(initialize_entity(ename=ename))
        try:
            df = pd.read_csv(csvs[ename], index_col=0)
        except:
            pass
        return df
    else:
        error = 'Cannot itialize entity %s' % ename
        print error
        sys.exit(1)


def store_df(new_df, stored=pd.DataFrame(), ename=None):
    # skip storing if no new data are passed.
    if not new_df.empty:
        if ename == 'session':
            new_sessions = new_df.drop('session', axis=1)

            if not stored.empty:
                sessions = stored.append(new_sessions)
            else:
                sessions = new_sessions
            sessions.to_csv(csvs[ename])

        elif ename in ['pilot', 'unit']:
            if not stored.empty:
                df = stored.append(new_df)
            else:
                df = new_df
            df.reset_index(inplace=True, drop=True)
            df.to_csv(csvs[ename])

        else:
            error = 'Cannot store DF to %s' % ename
            print error
            sys.exit(1)
    else:
        print 'WARNING: attempting to store an empty DF.'


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
    literals = [l for l in words if not
                any((number in set('0123456789')) for number in l)]

    # Check for exceptions:
    # a. every word of the domain name has a number
    if len(literals) == 0:

        # Some hostname use '-' instead of '.' as word separator.
        # The parser would have returned a single word and the
        # any of that word may have a number.
        if '-' in host[0]:
            words = host[0].split('-')
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

    # FIXME: When everything else fails, ad hoc manipulations of
    #        domain string.
    if 'its.osg' in domain:
        domain = 'its.osg'
    elif 'nodo' in domain:
        domain = 'nodo'
    elif 'bu.edu' in domain:
        domain = 'bu.edu'

    return domain


def load_new_sessions(datadir, pdm, udm):
    print '\nLoading sessions:'
    # Collect the RA objects and return them as a column of the sessions DF.
    sras = {}

    # Get sessions ID, experiment number and RA object. Assume:
    # datadir/exp*/sessiondir/session.json.
    start = datadir.rfind(os.sep) + 1
    for path, dirs, _ in os.walk(datadir):
        folders = path[start:].split(os.sep)

        # Use only exp*/rp.session.* paths.
        # TODO: find a better way to traverse dirtree on disk.
        if len(folders) == 2:
            sid = os.path.basename(glob.glob('%s/*.json' % path)[0])[:-5]

            # Check whether SID of json file name is consistent with SID of
            # directory name.
            if sid == folders[1]:

                # RA objects cannot be serialize: every RA session object need
                # to be constructed at every run.
                # TODO: Make RA session objects serializable in msgpack format.
                sra = ra.Session(sid, 'radical.pilot', src=path)
                sras[sid] = sra

                # Skip session if we have already saved it on disk. No need to
                # recompute all the durations and properties for the session
                # but we need to add the RA session object back to the stored
                # sessions DF.
                stored_sessions = load_df(ename='session')
                if sid in stored_sessions.index.tolist():
                    stored_sessions.loc[sid, 'session'] = sra
                    print '%s --- %s already stored in %s' % \
                        (folders[0], sid, csvs['session'])
                    continue

                # Initialize data structures for session DF when a session ID
                # is found that has not yet been stored.
                ss = initialize_entity(ename='session')
                sids = []  # Index of sessions DF
                sids.append(sid)

                # Session properties
                sp = sra.filter(etype='pilot', inplace=False)
                su = sra.filter(etype='unit', inplace=False)
                ss['session'].append(sra)
                ss['experiment'].append(folders[0])
                ss['TTC'].append(sra.ttc)
                ss['nhost'].append(None)
                ss['nunit'].append(len(su.get()))
                ss['npilot'].append(len(sp.get()))
                ss['npilot_active'].append(
                    len(sp.timestamps(state='PMGR_ACTIVE')))

                # Pilots total durations.  NOTE: ss initialization guarantees
                # the existence of keys.
                for duration in pdm.keys():
                    ss[duration].append(sp.duration(pdm[duration]))

                # Units total durations. NOTE: ss initialization guarantees the
                # existence of ss keys.
                for duration in udm.keys():
                    ss[duration].append(su.duration(udm[duration]))

                # Store session DF to csv.
                session = pd.DataFrame(ss, index=sids)
                store_df(session, stored=stored_sessions, ename='session')
                print '%s --- %s stored in %s' % \
                    (folders[0], sid, csvs['session'])
            else:
                error = 'ERROR: session folder and json file name differ'
                print '%s: %s != %s' % (error, folders[1], sid)

    # Add RA session objects to the df loaded from disk.
    for sid in sras.keys():
        stored_sessions.loc[sid, 'session'] = sras[sid]

    return stored_sessions


def add_session_unique_hosts(sessions, pilots):
    print '\n\nAdding number of unique hosts to sessions:'
    for sid in sessions.index:
        if pd.isnull(sessions.loc[sid]['nhost']):
            sessions.loc[sid, 'nhost'] = len(
                pilots[pilots['sid'] == sid]['hid'].unique())
            store_df(sessions, ename='session')
            sys.stdout.write('\n%s: %s hosts, stored in %s.' %
                             (sid, sessions.loc[sid]['nhost'], csvs['pilot']))

        else:
            sys.stdout.write('\n%s: %s hosts already stored in %s' %
                             (sid, sessions.loc[sid]['nhost'], csvs['pilot']))
    return sessions


def add_unit_hosts(units, pilots, sessions):
    print '\n\nAdding host and pilot IDs to units:'
    counter = 0
    for sid in sessions.index:
        sra = sessions.loc[sid]['session']
        pu_rels = sra.describe('relations', ['pilot', 'unit'])
        uids = units[units['sid'] == sid]['uid']
        for uid in uids:
            uix = units[(units['sid'] == sid) & (units['uid'] == uid)].index[0]
            if pd.isnull(units.loc[uix]['hid']):
                punit = [key[0] for key in pu_rels.items() if uid in key[1]][0]
                hid = pilots[(pilots['sid'] == sid) & (pilots['pid'] == punit)]['hid'].tolist()[0]
                units.loc[uix, 'pid'] = punit
                units.loc[uix, 'hid'] = hid
                counter += 1
            else:
                sys.stdout.write('\n%s:%s host ID already stored in %s' %
                                 (sid, uid, csvs['unit']))

    if counter:
        store_df(units, ename='unit')
        sys.stdout.write('\n%s: %s host and pilot IDs stored in %s.' %
                         (sid, counter, csvs['unit']))

    return units


def load_new_pilots(pdm, sessions):
    print '\n\nLoading pilots:'
    stored_pids = []

    # Calculate the duration for each state of each pilot of each run and
    # Populate the DataFrame  structure.
    for sid in sessions.index:
        sys.stdout.write('\n%s --- %s' % (sessions.loc[sid, 'experiment'], sid))
        ps = initialize_entity(ename='pilot')
        stored_pilots = load_df(ename='pilot')
        if not stored_pilots['sid'].empty:
            stored_pids = stored_pilots[
                stored_pilots['sid'] == sid]['pid'].values.tolist()

        # Derive properties of each session's pilot.
        s = sessions.loc[sid, 'session'].filter(etype='pilot', inplace=False)
        for pid in sorted(s.list('uid')):
            # Skip session if its pilots have been already stored.
            if pid in stored_pids:
                sys.stdout.write('\n%s already stored in %s' %
                                 (pid, csvs['pilot']))
                continue

            sys.stdout.write('\n' + pid + ': ')
            ps['pid'].append(pid)
            ps['sid'].append(sid)
            ps['experiment'].append(sessions.loc[sid, 'experiment'])

            # Derive host ID for each pilot.
            sf = s.filter(uid=pid, inplace=False)
            pentity = sf.get(etype=['pilot'])[0]
            if pentity.cfg['hostid']:
                ps['hid'].append(parse_osg_hostid(pentity.cfg['hostid']))
            else:
                ps['hid'].append(None)

            # Derive durations of each session's pilot.
            for duration in pdm.keys():
                if duration not in ps.keys():
                    ps[duration] = []
                if (not sf.timestamps(state=pdm[duration][0]) or
                        not sf.timestamps(state=pdm[duration][1])):
                    ps[duration].append(None)
                    continue
                ps[duration].append(sf.duration(pdm[duration]))
                sys.stdout.write('.')
        # Store session DF to csv.
        if ps['pid']:
            pilots = pd.DataFrame(ps)
            store_df(pilots, stored=stored_pilots, ename='pilot')
            print '\nstored in %s.' % csvs['pilot']

    # Return new DF merged into the one already stored (possibly empty).
    return stored_pilots


# TODO: Repeated code.
def load_new_units(udm, sessions):
    print '\nLoading units:'
    stored_uids = []

    # Calculate the duration for each state of each pilot of each run and
    # Populate the DataFrame  structure.
    for sid in sessions.index:
        sys.stdout.write('\n%s --- %s' % (sessions.loc[sid, 'experiment'], sid))

        us = initialize_entity(ename='unit')
        stored_units = load_df(ename='unit')
        if not stored_units['sid'].empty:
            stored_uids = stored_units[
                stored_units['sid'] == sid]['uid'].values.tolist()

        # Derive properties of each session's pilot.
        s = sessions.loc[sid, 'session'].filter(etype='unit', inplace=False)
        for uid in sorted(s.list('uid')):

            # Skip session if its pilots have been already stored.
            if uid in stored_uids:
                sys.stdout.write('\n%s already stored in %s' %
                                 (uid, csvs['unit']))
                continue

            sys.stdout.write('\n' + uid + ': ')
            us['uid'].append(uid)
            us['sid'].append(sid)
            us['hid'].append(None)
            us['experiment'].append(sessions.loc[sid, 'experiment'])

            # Derive durations of each session's pilot.
            sf = s.filter(uid=uid, inplace=False)
            for duration in udm.keys():
                if duration not in us.keys():
                    us[duration] = []
                if (not sf.timestamps(state=udm[duration][0]) or
                        not sf.timestamps(state=udm[duration][1])):
                    us[duration].append(None)
                    continue
                us[duration].append(sf.duration(udm[duration]))
                sys.stdout.write('.')
        # Store session DF to csv.
        if us['uid']:
            units = pd.DataFrame(us)
            store_df(units, stored=stored_units, ename='unit')
            print '\nstored in %s.' % csvs['unit']

    # Return new DF merged into the one already stored (possibly empty).
    return stored_units


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    datadir = '../data/'

    # Global constants
    # File names where to save the DF of each entity of each session.
    csvs = {'session': '%ssessions.csv' % datadir,
            'pilot'  : '%spilots.csv' % datadir,
            'unit'   : '%sunits.csv' % datadir}

    # Model of pilot durations.
    pdm = {'P_PMGR_SCHEDULING': ['NEW',
                                 'PMGR_LAUNCHING_PENDING'],
           'P_PMGR_QUEUING'   : ['PMGR_LAUNCHING_PENDING',
                                 'PMGR_LAUNCHING'],
           'P_LRMS_SUBMITTING': ['PMGR_LAUNCHING',
                                 'PMGR_ACTIVE_PENDING'],
           'P_LRMS_QUEUING'   : ['PMGR_ACTIVE_PENDING',
                                 'PMGR_ACTIVE'],
           'P_LRMS_RUNNING'   : ['PMGR_ACTIVE',
                                 ['DONE', 'CANCELED', 'FAILED']]}

    # Model of unit durations.
    udm = {'U_UMGR_SCHEDULING'   : ['NEW',
                                    'UMGR_SCHEDULING_PENDING'],
           'U_UMGR_BINDING'      : ['UMGR_SCHEDULING_PENDING',
                                    'UMGR_SCHEDULING'],
           #    'I_UMGR_SCHEDULING'   : ['UMGR_SCHEDULING',
           #                             'UMGR_STAGING_INPUT_PENDING'],
           #    'I_UMGR_QUEING'       : ['UMGR_STAGING_INPUT_PENDING',
           #                             'UMGR_STAGING_INPUT'],
           #    'I_AGENT_SCHEDULING'  : ['UMGR_STAGING_INPUT',
           #                             'AGENT_STAGING_INPUT_PENDING'],
           #    'I_AGENT_QUEUING'     : ['AGENT_STAGING_INPUT_PENDING',
           #                             'AGENT_STAGING_INPUT'],
           #    'I_AGENT_TRANSFERRING': ['AGENT_STAGING_INPUT',
           #                             'AGENT_SCHEDULING_PENDING'],
           'U_AGENT_QUEUING'     : ['AGENT_SCHEDULING_PENDING',
                                    'AGENT_SCHEDULING'],
           'U_AGENT_SCHEDULING'  : ['AGENT_SCHEDULING',
                                    'AGENT_EXECUTING_PENDING'],
           'U_AGENT_QUEUING_EXEC': ['AGENT_EXECUTING_PENDING',
                                    'AGENT_EXECUTING'],
           'U_AGENT_EXECUTING'   : ['AGENT_EXECUTING',
                                    'AGENT_STAGING_OUTPUT_PENDING']}
    #    'O_AGENT_QUEUING'     : ['AGENT_STAGING_OUTPUT_PENDING',
    #                             'AGENT_STAGING_OUTPUT'],
    #    'O_UMGR_SCHEDULING'   : ['AGENT_STAGING_OUTPUT',
    #                             'UMGR_STAGING_OUTPUT_PENDING'],
    #    'O_UMGR_QUEUING'      : ['UMGR_STAGING_OUTPUT_PENDING',
    #                             'UMGR_STAGING_OUTPUT'],
    #    'O_UMGR_TRANSFERRING' : ['UMGR_STAGING_OUTPUT',
    #                             ['DONE', 'CANCELED', 'FAILED']]}

    # stored_sessions = load_df(sessions_csv, ss)
    sessions = load_new_sessions(datadir, pdm, udm)
    pilots = load_new_pilots(pdm, sessions)
    units = load_new_units(udm, sessions)

    # Add values across DFs.
    sessions = add_session_unique_hosts(sessions, pilots)
    units = add_unit_hosts(units, pilots, sessions)
