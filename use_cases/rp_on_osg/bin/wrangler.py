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


def load_stored_sessions(datadir, filecsv, sessions):
    try:
        sessions = pd.read_csv(filecsv, index_col=0)
    except:
        print "WARNING: File %s is empty or not valid." % datadir
    print sessions
    return sessions


def load_new_sessions(datadir, stored_ids):
    sids = []
    sras = []
    ttcs = []
    paths = []
    nunits = []
    experiments = []

    # Get sessions ID from .json file names. Assume:
    # datadir/exp*/sessiondir/session.json
    start = datadir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(datadir):
        folders = path[start:].split(os.sep)
        if len(folders) == 2:
            sid = os.path.basename(glob.glob('%s/*.json' % path)[0])[:-5]
            if sid in stored_ids:
                continue
            sra = ra.Session(sid, 'radical.pilot', src=path)
            ttc = sra.ttc
            units = sra.filter(etype='unit', inplace=False).get()
            if sid == folders[1]:
                sids.append(sid)
                sras.append(sra)
                ttcs.append(ttc)
                paths.append(path)
                nunits.append(len(units))
                experiments.append(folders[0])
            else:
                error = 'ERROR: session folder and json file name differ'
                print '%s: %s != %s' % (error, folders[1], sid)

    sessions = pd.DataFrame({'session': sras,
                             'experiment': experiments,
                             'TTC': ttcs,
                             'nunit': nunits},
                            index=sids)
    return sessions


def sessions_TTC():
    pass


def sessions_nunits():
    pass


if __name__ == '__main__':
    datadir = '../data/'
    sessions_csv = '%s/sessions.csv' % datadir

    sessions_df = pd.DataFrame({'session'   : [],
                                'experiment': [],
                                'TTC'       : [],
                                'nunit'     : []})

    stored_sessions = load_stored_sessions(datadir, sessions_csv, sessions_df)
    new_sessions = load_new_sessions(datadir, stored_sessions.index.tolist())
    sessions = stored_sessions.append(new_sessions)

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
