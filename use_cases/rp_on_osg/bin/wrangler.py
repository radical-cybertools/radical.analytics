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


def load_stored_sessions(datadir, filecsv):
    sessions = pd.DataFrame({  # 'SID': [],
                             'session': [],
                             'experiment': []})
    try:
        sessions = pd.read_csv(filecsv, index_col=0)
    except:
        print "WARNING: File %s is empty or not valid." % datadir
    print sessions
    sys.exit(0)
    return sessions


def load_new_sessions(datadir, stored_ids):
    sids = []
    paths = []
    experiments = []
    sras = []

    # Get sessions ID from .json file names. Assume:
    # datadir/exp*/sessiondir/session.json
    start = datadir.rfind(os.sep)+1
    for path, dirs, files in os.walk(datadir):
        folders = path[start:].split(os.sep)
        if len(folders) == 2:
            sid = os.path.basename(glob.glob('%s/*.json' % path)[0])[:-5]
            if sid in stored_ids:
                continue

            if sid == folders[1]:
                sids.append(sid)
                paths.append(path)
                experiments.append(folders[0])
                sras.append(ra.Session(sid, 'radical.pilot', src=path))

            else:
                error = 'ERROR: session folder and json file name differ'
                print '%s: %s != %s' % (error, folders[1], sid)

    sessions = pd.DataFrame({  # 'SID': sids,
                             'session': sras,
                             'experiment': experiments},
                            index=sids)

    return sessions


def load_sessions(datadir, filecsv):
    stored_sessions = load_stored_sessions(datadir, filecsv)
    new_sessions = load_new_sessions(datadir, stored_sessions.index.tolist())
    sessions = stored_sessions.append(new_sessions)
    return sessions


def sessions_TTC():
    pass


def sessions_nunits():
    pass


if __name__ == '__main__':
    datadir = '../data/'
    sessions_csv = '%s/sessions.csv' % datadir

    sessions = load_sessions(datadir, sessions_csv)

    print sessions

    # Save session DataFrame to a csv file.
    sessions.to_csv(sessions_csv)  # , index=False)

    # Populate sessions DataFrame with derivative values
    # Time To Completion (TTC)
    # for sid in sessions['SID'].values:
    #     if 'TTC' in sessions.columns:
    #         if sessions[sessions['SID'] == sid]['TTC']:
    #             print 'Ciao'
    #             continue
    #     # sessions[sessions['SID'] == sid]['TTC'] = sessions[sessions['SID'] == sid]['session'].values.ttc
    #     print sessions[sessions['SID'] == sid]['session'].values[0].ttc
    # sessions

    # Save session DataFrame to a csv file.
    # sessions.to_csv(dfspaths['sessions'], index=False)
    #
    # # Number of units for each session (nunit)
    # for sid in sessions.index:
    #     nunit = sessions.ix[sid, 'session'].filter(etype='unit',
    #                                                inplace=False).get()
    #     sessions.ix[sid, 'nunit'] = len(nunit)
    #
    # # Save session DataFrame to a csv file.
    # sessions.to_csv(dfspaths['sessions'])

    # # Pilots
