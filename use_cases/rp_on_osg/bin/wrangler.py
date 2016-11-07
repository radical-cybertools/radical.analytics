#!/usr/bin/env python
"""This script does x.

Example:

Attributes:

Todo:

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import os
import glob
import sys
import pandas as pd
import radical.analytics as ra


def load_stored_sessions(filecsv, sessions):
    try:
        sessions = pd.read_csv(filecsv, index_col=0)
    except:
        print "WARNING: File %s is empty or not valid." % filecsv
    return sessions


def load_new_sessions(datadir, ttpdm, ttudm, stored_sessions):
    sids = []            # Sessions ID
    sras = []            # Sessions RA objects
    ttcs = []            # Sessions TTC
    paths = []           # Paths of sessions on disk
    nunits = []          # Sessions number of units
    npilots = []         # Sessions number of pilots
    experiments = []     # Sessions experiment
    npilots_active = []  # Sessions number of active pilots

    pt_l_sc = []         # Pilots total PMGR scheduling time
    pt_l_qs = []         # Pilots total PMGR queueing time
    pt_l_ss = []         # Pilots total PMGR submission time
    pt_r_qs = []         # Pilots total LRMS queueing time
    pt_r_rs = []         # Pilots total LRMS running time

    ut_l_ss = []         # Units total UMGR scheduling time
    ut_l_bs = []         # Units total UMGR binding time
    ut_r_qs = []         # Units total AGENT queueing time
    ut_r_ss = []         # Units total AGENT scheduling time
    ut_r_qxs = []        # Units total AGENT queueing time for execution
    ut_r_xs = []         # Units total AGENT execution time

    # Get sessions ID, experiment number and RA object. Assume:
    # datadir/exp*/sessiondir/session.json.
    start = datadir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(datadir):
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

                # Skip session if we have already saved it on disk. No need to
                # recompute all the durations and properties for the session
                # but we need to add the RA session object back to the stored
                # sessions DF.
                if sid in stored_sessions.index.tolist():
                    stored_sessions.ix[sid, 'session'] = sra
                    continue

                sp = sra.filter(etype='pilot', inplace=False)
                su = sra.filter(etype='unit', inplace=False)

                # Session properties
                sras.append(sra)
                sids.append(sid)
                ttcs.append(sra.ttc)
                paths.append(path)
                nunits.append(len(su.get()))
                npilots.append(len(sp.get()))
                experiments.append(folders[0])
                npilots_active.append(len(sp.timestamps(state='PMGR_ACTIVE')))

                # Pilots total durations
                pt_l_sc.append(sp.duration(ttpdm['ttp_pmgr_scheduling']))
                pt_l_qs.append(sp.duration(ttpdm['ttp_pmgr_queuing']))
                pt_l_ss.append(sp.duration(ttpdm['ttp_lrms_submitting']))
                pt_r_qs.append(sp.duration(ttpdm['ttp_lrms_queuing']))
                pt_r_rs.append(sp.duration(ttpdm['ttp_lrms_running']))

                # Units total durations
                ut_l_ss.append(su.duration(ttudm['ttu_umgr_scheduling']))
                ut_l_bs.append(su.duration(ttudm['ttu_umgr_binding']))
                ut_r_qs.append(su.duration(ttudm['ttu_agent_queuing']))
                ut_r_ss.append(su.duration(ttudm['ttu_agent_scheduling']))
                ut_r_qxs.append(su.duration(ttudm['ttu_agent_queuing_exec']))
                ut_r_xs.append(su.duration(ttudm['ttu_agent_executing']))
            else:
                error = 'ERROR: session folder and json file name differ'
                print '%s: %s != %s' % (error, folders[1], sid)

    # Create sessions Pandas DataFrame.
    new_sessions = pd.DataFrame({'session'               : sras,
                                 'experiment'            : experiments,
                                 'TTC'                   : ttcs,
                                 'nunit'                 : nunits,
                                 'npilot'                : npilots,
                                 'npilot_active'         : npilots_active,
                                 'ttp_pmgr_scheduling'   : pt_l_sc,
                                 'ttp_pmgr_queuing'      : pt_l_qs,
                                 'ttp_lrms_submitting'   : pt_l_ss,
                                 'ttp_lrms_queuing'      : pt_r_qs,
                                 'ttp_lrms_running'      : pt_r_rs,
                                 'ttu_umgr_scheduling'   : ut_l_ss,
                                 'ttu_umgr_binding'      : ut_l_bs,
                                 'ttu_agent_queuing'     : ut_r_qs,
                                 'ttu_agent_scheduling'  : ut_r_ss,
                                 'ttu_agent_queuing_exec': ut_r_qxs,
                                 'ttu_agent_executing'   : ut_r_xs},
                                index=sids)

    return stored_sessions.append(new_sessions)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    datadir = '../data/'
    objdir = '../data/ra_objects'
    sessions_csv = '%s/sessions.csv' % datadir

    sessions_df = pd.DataFrame({'session'               : [],
                                'experiment'            : [],
                                'TTC'                   : [],
                                'nunit'                 : [],
                                'npilot'                : [],
                                'npilot_active'         : [],
                                'ttp_pmgr_scheduling'   : [],
                                'ttp_pmgr_queuing'      : [],
                                'ttp_lrms_submitting'   : [],
                                'ttp_lrms_queuing'      : [],
                                'ttp_lrms_running'      : [],
                                'ttu_umgr_scheduling'   : [],
                                'ttu_umgr_binding'      : [],
                                'ttu_agent_queuing'     : [],
                                'ttu_agent_scheduling'  : [],
                                'ttu_agent_queuing_exec': [],
                                'ttu_agent_executing'   : []})

    # Model of TOTAL pilot durations.
    ttpdm = {'ttp_pmgr_scheduling': ['NEW',
                                     'PMGR_LAUNCHING_PENDING'],
             'ttp_pmgr_queuing'   : ['PMGR_LAUNCHING_PENDING',
                                     'PMGR_LAUNCHING'],
             'ttp_lrms_submitting': ['PMGR_LAUNCHING',
                                     'PMGR_ACTIVE_PENDING'],
             'ttp_lrms_queuing'   : ['PMGR_ACTIVE_PENDING',
                                     'PMGR_ACTIVE'],
             'ttp_lrms_running'   : ['PMGR_ACTIVE',
                                     ['DONE', 'CANCELED', 'FAILED']]}

    # Model of total unit durations.
    ttudm = {'ttu_umgr_scheduling'   : ['NEW',
                                        'UMGR_SCHEDULING_PENDING'],
             'ttu_umgr_binding'      : ['UMGR_SCHEDULING_PENDING',
                                        'UMGR_SCHEDULING'],
             'tti_umgr_scheduling'   : ['UMGR_SCHEDULING',
                                        'UMGR_STAGING_INPUT_PENDING'],
             'tti_umgr_queing'       : ['UMGR_STAGING_INPUT_PENDING',
                                        'UMGR_STAGING_INPUT'],
             'tti_agent_scheduling'  : ['UMGR_STAGING_INPUT',
                                        'AGENT_STAGING_INPUT_PENDING'],
             'tti_agent_queuing'     : ['AGENT_STAGING_INPUT_PENDING',
                                        'AGENT_STAGING_INPUT'],
             'tti_agent_transferring': ['AGENT_STAGING_INPUT',
                                        'AGENT_SCHEDULING_PENDING'],
             'ttu_agent_queuing'     : ['AGENT_SCHEDULING_PENDING',
                                        'AGENT_SCHEDULING'],
             'ttu_agent_scheduling'  : ['AGENT_SCHEDULING',
                                        'AGENT_EXECUTING_PENDING'],
             'ttu_agent_queuing_exec': ['AGENT_EXECUTING_PENDING',
                                        'AGENT_EXECUTING'],
             'ttu_agent_executing'   : ['AGENT_EXECUTING',
                                        'AGENT_STAGING_OUTPUT_PENDING'],
             'tto_agent_queuing'     : ['AGENT_STAGING_OUTPUT_PENDING',
                                        'AGENT_STAGING_OUTPUT'],
             'tto_umgr_scheduling'   : ['AGENT_STAGING_OUTPUT',
                                        'UMGR_STAGING_OUTPUT_PENDING'],
             'tto_umgr_queuing'      : ['UMGR_STAGING_OUTPUT_PENDING',
                                        'UMGR_STAGING_OUTPUT'],
             'tto_umgr_transferring' : ['UMGR_STAGING_OUTPUT',
                                        ['DONE', 'CANCELED', 'FAILED']]}

    stored_sessions = load_stored_sessions(sessions_csv, sessions_df)
    sessions = load_new_sessions(datadir, ttpdm, ttudm, stored_sessions)

    print sessions

    save_sessions = sessions.drop('session', axis=1)
    save_sessions.to_csv(sessions_csv)
