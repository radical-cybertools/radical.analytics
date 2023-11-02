
from .session import Session

from typing import List, Union


# ------------------------------------------------------------------------------
#
class Experiment(object):

    # --------------------------------------------------------------------------
    #
    def __init__(self, sessions: List[Union[str, Session]],
                       stype: str = None):
        '''
        This class represents an RCT experiment, i.e., a series of RA sessions
        which are collectively analyzed.

        `sessions` is expected to be either (1) a list of session source paths
        pointing to tarballs or session directories, or (b) a list of
        `ra.Session` instances.  The order of entries in the list determines the
        default order used in plots etc.

        The session type `stype` will be uniformely applied when reading session
        data from provided paths.
        '''

        # FIXME: this is missing an abstraction: `Run`: a collection of sessions
        #         which share the same parameters and thus can be statistically
        #         handled together (means, std-deviation, etc).  Right now we
        #         only use this `Experiment` abstraction for non-statistical
        #         analysis (event plots, utilization plots, etc.)

        self._sessions = list()

        if not sessions:
            raise ValueError('cannot create experiments w/o sessions')

        if isinstance(sessions[0], str):
            for src in sessions:
                assert isinstance(src, str)
                self._sessions.append(Session.create(src=src, stype=stype))

        else:
            for session in sessions:
                assert isinstance(session, Session)
                self._sessions.append(session)


    # --------------------------------------------------------------------------
    #
    @property
    def sessions(self):
        return self._sessions

    @property
    def sids(self):
        return [s.sid for s in self._sessions]


    # --------------------------------------------------------------------------
    #
    def utilization(self, metrics, rtype='cpu', udurations=None):
        '''
        return five dictionaries:
          - provided resources
          - consumed resources
          - absolute stats
          - relative stats
          - information about resource utilization

        The resource dictionaries have the following structures::

            provided = {
                <session_id> : {
                    'metric_1' : {
                        'uid_1'        : [float, list],
                        'uid_2'        : [float, list],
                        ...
                    },
                    'metric_2' : {
                        'uid_1'        : [float, list],
                        'uid_2'        : [float, list],
                        ...
                    },
                    ...
                },
                ...
            }
            consumed = {
                <session_id> : {
                    'metric_1' : {
                        'uid_1'         : [float, list]
                        'uid_2'         : [float, list],
                        ...
                    },
                    'metric_2' :         {
                        'uid_1'         : [float, list],
                        'uid_2'         : [float, list],
                        ...
                    },
                    ...
                },
                ...
            }

        `float` is always in tasks of `resource * time`, (think `core-hours`),
        `list` is a list of 4-tuples `[t0, t1, r0, r1]` which signify at what
        specific time interval (`t0 to t1`) what specific resources (`r0 to r1`)
        have been used.  The task of the resources are here dependent on the
        session type: only RP sessions are supported at the moment where those
        resource values are indexes in to the list of cores used in that
        specific session (offset over multiple pilots, if needed).
        '''

        # FIXME: the data structure documented above is not yet implemented

        provided  = dict()
        consumed  = dict()
        stats_abs = dict()
        stats_rel = dict()
        info      = dict()

        # obtain resources provisions and consumptions for all sessions
        for session in self._sessions:

            sid = session.uid
            p, c, sa, sr, i = session.utilization(metrics, rtype, udurations)

            provided [sid] = p
            consumed [sid] = c
            stats_abs[sid] = sa
            stats_rel[sid] = sr
            info     [sid] = i

        return provided, consumed, stats_abs, stats_rel, info


    # --------------------------------------------------------------------------
    #
    def _dump_ts(self, dname, e, spec, psize=0):

        pass
      # ts   = e.timestamps(event=spec)
      # diff = ts[-1] - ts[0]
      # print '%-10s : %-55s : %3d : %10.1f - %10.1f = %10.1f -> %10.1f' \
      #     % (dname, spec, len(ts), ts[-1], ts[0], diff, diff * psize)


# ------------------------------------------------------------------------------

