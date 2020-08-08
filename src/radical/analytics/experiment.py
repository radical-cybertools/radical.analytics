
from .session import Session


# ------------------------------------------------------------------------------
#
class Experiment(object):

    # --------------------------------------------------------------------------
    #
    def __init__(self, sources, stype):
        '''
        This class represents an RCT experiment, i.e., a series of RA sessions
        which are collectively analyzed.

        `sources` is expected to be a list of tuples of session source paths
        pointing to tarballs or session directories.  The order of tuples in the
        list determines the default order used in plots etc.

        The session type `stype` will be uniformely applied to all sessions.
        '''

        # FIXME: this is missing an abstraction: `Run`: a collection of sessions
        #         which share the same parameters and thus can be statistically
        #         handled together (means, std-deviation, etc).  Right now we
        #         only use this `Experiment` abstraction for non-statistical
        #         analysis (event plots, utilization plots, etc.)

        self._sessions = list()

        for src in sources:
            self._sessions.append(Session.create(src=src, stype=stype))


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
    def utilization(self, metrics):
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

        `float` is always in units of `resource * time`, (think `core-hours`),
        `list` is a list of 4-tuples `[t0, t1, r0, r1]` which signify at what
        specific time interval (`t0 to t1`) what specific resources (`r0 to r1`)
        have been used.  The unit of the resources are here dependent on the
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
            p, c, sa, sr, i = session.utilization(metrics)

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

