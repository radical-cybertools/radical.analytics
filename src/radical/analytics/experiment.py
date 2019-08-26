
import radical.utils as ru
import radical.pilot as rp

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
        return two dictionaries, one for provided resources, one for consumed
        resources, with the following structures:

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
        session type - only RP sessions are supported at the moment where those
        resource values are indexes in to the list of cores used in that
        specific session (offset over multiple pilots, if needed).
        '''

        # FIXME: the data structure documented above is not yet implemented

        provided = dict()
        consumed = dict()
        stats    = dict()

        # obtain resources provisions and consumptions for all sessions
        for session in self._sessions:

            sid = session.uid
            provided[sid] = rp.utils.get_provided_resources(session)
            consumed[sid] = rp.utils.get_consumed_resources(session)

            total = 0.0
            stats[sid] = {'total': 0.0}

            for pid in provided[sid]['total']:
                for box in provided[sid]['total'][pid]:
                    stats[sid]['total'] += (box[1] - box[0]) * (box[3] - box[2])
            total = stats[sid]['total']

            for metric in metrics:
                if isinstance(metric, list):
                    name  = metric[0]
                    parts = metric[1]
                else:
                    name  = metric
                    parts = [metric]

                if name not in stats[sid]:
                    stats[sid][name] = 0.0
                for part in parts:
                    for uid in consumed[sid][part]:
                        for box in consumed[sid][part][uid]:
                            stats[sid][name] += (box[1] - box[0]) * (box[3] - box[2])

            print
            print '%s [%d]' % (sid, len(session.get(etype='unit')))
            for metric in metrics + ['total']:
                if isinstance(metric, list):
                    name  = metric[0]
                    parts = metric[1]
                else:
                    name  = metric
                    parts = ''

                val = stats[sid][name]
                if val == 0.0: glyph = '!'
                else         : glyph = ''
                rel = 100.0 * val / total
                print '    %-20s: %14.3f  %6.1f%%  %2s  %s' \
                    % (name, val, rel, glyph, parts)

            have = 0.0
            over = 0.0
            work = 0.0
            for metric in sorted(stats[sid].keys()):
                if metric == 'total':
                    have  += stats[sid][metric]
                else:
                    if metric == 'Execution Cmd':
                        work  += stats[sid][metric]
                    else:
                        over  += stats[sid][metric]

                miss = have - over - work

                rel_over = 100.0 * over / total
                rel_work = 100.0 * work / total
                rel_miss = 100.0 * miss / total

            print
            print '    %-20s: %14.3f  %6.1f%%' % ('total', have, 100.0)
            print '    %-20s: %14.3f  %6.1f%%' % ('over',  over, rel_over)
            print '    %-20s: %14.3f  %6.1f%%' % ('work',  work, rel_work)
            print '    %-20s: %14.3f  %6.1f%%' % ('miss',  miss, rel_miss)

            stats[sid]['Other'] = miss

        return provided, consumed, stats


    # --------------------------------------------------------------------------
    #
    def _dump_ts(self, dname, e, spec, psize=0):

        pass
      # ts   = e.timestamps(event=spec)
      # diff = ts[-1] - ts[0]
      # print '%-10s : %-55s : %3d : %10.1f - %10.1f = %10.1f -> %10.1f' \
      #     % (dname, spec, len(ts), ts[-1], ts[0], diff, diff * psize)


# ------------------------------------------------------------------------------

