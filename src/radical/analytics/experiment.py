
import radical.utils as ru
import radical.pilot as rp

from .session import Session

# TODO: an RP agent is just another consumer of resources, as ist the pilot
#       itself.  Oncethis is properly abstracted, we don't need to know
#       ORDERED_KEYS anymore


# ------------------------------------------------------------------------------
#
# absolute utilization: number of core hours per activity
# relative utilization: percentage of total pilot core hours
#
ABSOLUTE = False

PILOT_DURATIONS   = rp.utils.PILOT_DURATIONS
UNIT_DURATIONS    = rp.utils.UNIT_DURATIONS
DERIVED_DURATIONS = rp.utils.DERIVED_DURATIONS
ORDERED_KEYS      = rp.utils.ORDERED_KEYS


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
    def utilization(self, provider, consumer):
        '''
        return a dictionary with the following structure:

            {
              <session_id> : {
                   'resource' : {
                       'uid_1'        : [float, list],  # r_1
                       'uid_1'        : [float, list],  # r_2
                       ...
                       'total'        :  float,         # r_1 + r_2 + ... = 100%
                    },

                    'consumer': {
                       'uid_1' : {
                           'metric_1' : [float, list]   # c_1_1
                           'metric_2' : [float, list],  # c_1_2
                           ...
                        },
                       'uid_2' : {
                           'metric_1' : [float, list],  # c_2_1
                           'metric_2' : [float, list],  # c_2_2
                           ...
                        },
                        ...
                        'total'    : {
                           'metric_1' :  float,         # c_1_1 + c_2_1 + ...
                           'metric_2' :  float,         # c_2_1 + c_2_2 + ...
                           ...
                        },
                    },
                },
                ...  # more sessions
                'total' : {
                   'resource' : {
                       'total'    : float,
                    },
                    'consumer'    : {
                       'metric_1' : float,
                       'metric_2' : float,
                       ...
                    },
                }
            }

        `float` is always in units of `resource * time`, (think `core-hours`),
        `list` is a list of 4-tuples `[t0, t1, r0, r1]` which signify at what
        specific time interval (`t0 to t1`) what specific resources (`r0 to r1`)
        have been used.  The unit of the resources are here dependent on the
        session type - only RP sessions are supported at the moment where those
        resource values are indexes in to the list of cores used in that
        specific session (offset over multiple pilots, if needed).
        '''

        data        = dict()  # dict of contributions to utilization
        utilization = dict()  # final utilization

        for session in self._sessions:

            sid = session.uid
            print sid
            print

            # compute how many core-hours each duration consumed (or allocated,
            # wasted, etc - depending on the semantic type of duration)
            data[sid] = dict()

            for dname in PILOT_DURATIONS:
                data[sid][dname] = 0.0

            for dname in UNIT_DURATIONS:
                data[sid][dname] = 0.0

            # some additional durations we derive implicitly
            for dname in DERIVED_DURATIONS:
                data[sid][dname] = 0.0

            for pilot in session.get(etype='pilot'):

              # pprint.pprint(pilot.cfg)

                # we immediately take of the agent nodes, and change pilot_size
                # accordingly
                cpn = pilot.cfg['resource_details']['rm_info'] \
                                                   ['cores_per_node']
                psize  = pilot.description['cores']
                anodes = 0
                for agent in pilot.cfg.get('agents', []):
                    if pilot.cfg['agents'][agent].get('target') == 'node':
                        anodes += 1
                spec = PILOT_DURATIONS['p_total']
                if ru.STATE in spec and ru.EVENT not in spec:
                    spec[ru.EVENT] = 'state'
                try:
                    self._dump_ts(dname, pilot, spec)
                    walltime = pilot.duration(event=spec)
                except:
                    print 'missing p_total - fatal'
                    raise
                psize_full = psize
                psize      = psize_full - anodes * cpn

                data[sid]['p_total'] += walltime * psize_full
                data[sid]['p_agent'] += walltime * anodes * cpn

                print 'units      : %10d' % len(session.get(etype='unit'))
                print 'pilot size : %10d = %10d (avail) + %10d (agent) ' \
                      '[%d nodes]' % (psize_full, psize, anodes * cpn, anodes)
                print 'pilot resrc: %10.1f = %10.1f (avail) + %10.1f (agent)' \
                    % (walltime * psize_full, walltime * psize,
                       walltime * anodes * cpn)

                  # spec = PILOT_DURATIONS[dname]
                  # if ru.STATE in spec and ru.EVENT not in spec:
                  #     spec[ru.EVENT] = 'state'

                try:
                    spec = PILOT_DURATIONS['p_total']
                    self._dump_ts(dname, pilot, spec)
                    tot = pilot.duration(event=spec)
                except:
                    print 'no p_total - fatal'
                    raise
                print
                print 'pilot contributions (time):'
                print 'total          : %14.1f' % tot

                # now we can derive the utilization for all other pilot
                # durations specified.  Note that this is now off by some amount
                # for the bootstrapping step where we don't yet have sub-agents,
                # but that can be justified: the sub-agent nodes are explicitly
                # reserved for their purpose at that time. too.
                parts   = 0.0
                missing = set()
              # for dname in [
              #               'p_boot',
              #               'p_term',
              #               'p_setup_1',
              #               'p_uexec',
              #              ]:
                for dname in PILOT_DURATIONS:

                    if dname == 'p_total':
                        continue

                    spec = PILOT_DURATIONS[dname]
                    self._dump_ts(dname, pilot, spec, psize)
                    try:
                        dur = pilot.duration(event=spec)
                    except:
                        missing.add(dname)
                        dur = 0.0
                    parts += dur
                    print ' - %-10s  : %14.1f * %5d = %14.1f' \
                        % (dname, dur, psize, dur * psize)
                    data[sid][dname] += dur * psize
                print 'parts          : %14.1f' % parts
                print 'diff           : %14.1f' % (tot - parts)
                print

            if missing:
                for dname in sorted(list(missing)):
                    print 'missing pilot contributions: %s' % dname
            else:
                print 'pilot ok'


            # we do the same for the unit durations - but here we add up the
            # contributions for all individual units.
            missing = set()
            for unit in session.get(etype='unit'):
                usize  = unit.description['cpu_processes'] \
                       * unit.description['cpu_threads']
                uparts = 0.0
                utot   = 0.0
              # for e in unit.events:
              #     print e
                for dname in UNIT_DURATIONS:
                  # print dname
                    spec = UNIT_DURATIONS[dname]
                    if ru.STATE in spec and ru.EVENT not in spec:
                        spec[ru.EVENT] = 'state'
                    try:
                        dur = unit.duration(event=spec)
                    except:
                        missing.add(dname)
                        dur = 0.0
                    data[sid][dname] += dur * usize
                    if dname == 'u_total': utot   += dur
                    else                 : uparts += dur

                # sanity check
                udiff = 0
                if uparts != utot:
                    print '%s: %10.2f != %10.2f : %10.2f' \
                        % (unit.uid, uparts, utot, uparts - utot)
                    udiff += (uparts - utot)
                    for dname in UNIT_DURATIONS:
                        spec = UNIT_DURATIONS[dname]
                        if ru.STATE in spec and ru.EVENT not in spec:
                            spec[ru.EVENT] = 'state'
                        try:
                            dur = unit.duration(event=spec)
                        except:
                            print '? %s' % dname
                            dur = 0.0
                        print '%-15s'  % dname,
                        print '%20.5f' % dur


            if missing:
                for dname in sorted(list(missing)):
                    print 'missing unit  contributions: %s' % dname
                print

          # print 'udiff: %2f' % udiff
          # sys.exit()


            # ------------------------------------------------------------------
            #
            # sanity checks and derived values
            #
            # we add up 'p_setup_1' and 'p_setup_2' to 'p_setup'
            p_setup_1 = data[sid]['p_setup_1']
            p_setup_2 = data[sid]['p_setup_2']   # FIXME
            data[sid]['p_setup'] = p_setup_1 + p_setup_2
            del(data[sid]['p_setup_1'])
         #  del(data[sid]['p_setup_2'])

            # For both the pilot and the unit utilization, the
            # individual contributions must be the same as the total.
            tot    = data[sid]['p_total']
            print 'pilot contributions (resources):'
            print 'total          : %14.1f' % tot
            parts  = 0.0
            for p in data[sid]:
                if p != 'p_total' and not p.startswith('u_'):
                    parts += data[sid][p]
                    print ' - %-12s: %14.1f' % (p, data[sid][p])
            print 'diff           : %14.1f = %14.1f - %14.1f'\
                % (tot - parts, tot, parts)
            assert(abs(tot - parts) < 0.0001), '%s == %s' % (tot, parts)

            # same for unit consistency
            tot    = data[sid]['u_total']
            print
            print 'unit  contributions (resources):'
            print 'total          : %14.1f' % tot
            parts  = 0.0
            for p in data[sid]:
                if p != 'u_total' and not p.startswith('p_'):
                    parts += data[sid][p]
                    print ' - %-12s: %14.1f' % (p, data[sid][p])
            print 'diff           : %14.1f = %14.1f - %14.1f' \
                % (tot - parts, tot, parts)
            assert(abs(tot - parts) < 0.0001), '%s == %s' % (tot, parts)
            print

            # another sanity check: the pilot `p_uexec` data should always be
            # larger than the unit `total`.
            p_uexec = data[sid]['p_uexec']
            u_total = data[sid]['u_total']
            print 'p_total        : %14.1f > %14.1f = %14.1f%%' \
                    % (p_uexec, u_total, u_total * 100 / p_uexec)
            assert(p_uexec > u_total), '%s > %s' % (p_uexec, u_total)

            # We in fact know that the difference above, which is not explicitly
            # accounted for otherwise, is attributed to the agent component
            # overhead, and to the DB overhead: its the overhead to get from
            # a functional pilot to the first unit being scheduled, and from the
            # last unit being unscheduled to the pilot being terminated (witing
            # for other units to be finished etc).  We consider that time 'idle'
            data[sid]['p_idle' ] = p_uexec - u_total
            del(data[sid]['p_uexec'])
            print 'p_idle         : %14.1f' % data[sid]['p_idle']

            n_units = len(session.get(etype='unit'))
            p_size  = 0
            for pilot in session.get(etype='pilot'):
                p_size += pilot.description['cores']

            # check that the utilzation contributions add up to the total
            tot_abs = data[sid]['p_total']
            sum_abs = 0
            sum_rel = 0
            utilization[sid] = dict()
            for key in ORDERED_KEYS:
                util_abs = data[sid][key]
                util_rel = 100.0 * util_abs / tot_abs
                sum_abs += util_abs
                sum_rel += util_rel

                if ABSOLUTE: utilization[sid][key] = util_abs
                else       : utilization[sid][key] = util_rel

            print '%-40s  -- %10.2f -- %s' % (sid, sum_abs, (n_units, p_size))

            assert(abs(tot_abs - sum_abs) < 0.0001), (tot_abs, sum_abs)
            assert(abs(100.0   - sum_rel) < 0.0001), (100.0,   sum_rel)

        print

        return utilization


    # --------------------------------------------------------------------------
    #
    def _dump_ts(self, dname, e, spec, psize=0):

        pass
      # ts   = e.timestamps(event=spec)
      # diff = ts[-1] - ts[0]
      # print '%-10s : %-55s : %3d : %10.1f - %10.1f = %10.1f -> %10.1f' \
      #     % (dname, spec, len(ts), ts[-1], ts[0], diff, diff * psize)


# ------------------------------------------------------------------------------

