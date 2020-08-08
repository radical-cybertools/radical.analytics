
import sys
import pprint

import radical.utils as ru


# ------------------------------------------------------------------------------
#
class Entity(object):

    def __init__(self, _uid, _etype, _profile, _details):
        """
        Args:
            uid (:obj:str): an ID assumed to be unique in the scope of an RA
                Session
            etype (:obj:str): the type of the entity. This defines, amongst
                others, what event model the session will assume to be valid for
                this entity.
            profile: .
            details: .
        """

        assert(_uid)
        assert(_profile)

        self._uid         = _uid
        self._etype       = _etype
        self._details     = _details
        self._description = self._details.get('description', dict())
        self._cfg         = self._details.get('cfg',         dict())

        # FIXME: this should be sorted out on RP level
        self._cfg['hostid'] = self._details['hostid']

        self._states      = dict()
        self._events      = list()
        self._consistency = {'log'         : list(),
                             'state_model' : None,
                             'event_model' : None,
                             'timestamps'  : None}

        self._t_start     = None
        self._t_stop      = None
        self._ttc         = None

        self._initialize(_profile)


    # --------------------------------------------------------------------------
    #
    def __getstate__(self):

        state = {
                 'uid'         : self._uid,
                 'etype'       : self._etype,
                 'details'     : self._details,
                 'description' : self._description,
                 'cfg'         : self._cfg,

                 'states'      : self._states,
                 'events'      : self._events,
                 'consistency' : self._consistency,

                 't_start'     : self._t_start,
                 't_stop'      : self._t_stop,
                 'ttc'         : self._ttc,
                }

        return state


    # --------------------------------------------------------------------------
    #
    def __setstate__(self, state):

        self._uid          = state['uid']
        self._etype        = state['etype']
        self._details      = state['details']
        self._description  = state['description']
        self._cfg          = state['cfg']

        self._states       = state['states']
        self._events       = state['events']
        self._consistency  = state['consistency']

        self._t_start      = state['t_start']
        self._t_stop       = state['t_stop']
        self._ttc          = state['ttc']


    # --------------------------------------------------------------------------
    #
    @property
    def t_start(self):
        return self._t_start

    @property
    def t_stop(self):
        return self._t_stop

    @property
    def ttc(self):
        return self._ttc

    @property
    def t_range(self):
        return [self._t_start, self._t_stop]

    @property
    def uid(self):
        return self._uid

    @property
    def etype(self):
        return self._etype

    @property
    def states(self):
        return self._states

    @property
    def description(self):
        return self._description

    @property
    def cfg(self):
        return self._cfg

    @property
    def events(self):
        return self._events

    @property
    def consistency(self):
        return self._consistency


    # --------------------------------------------------------------------------
    #
    def __str__(self):

        return "ra.Entity [%s]: %s\n    states: %s" \
                % (self.etype, self.uid, list(self._states.keys()))


    # --------------------------------------------------------------------------
    #
    def __repr__(self):

        return str(self)


    # --------------------------------------------------------------------------
    #
    def _initialize(self, profile):

        # only call once
        assert (not self._states)
        assert (not self._events)

        if profile:
            self._t_start = sys.float_info.max
            self._t_stop  = sys.float_info.min

        # we expect each event tuple to have `time` and `event`, and expect
        # 'advance' events to signify a state transition.
        for event in sorted(profile, key=lambda x: (x[ru.TIME])):

            t = event[ru.TIME]

            self._t_start = min(self._t_start, t)
            self._t_stop  = max(self._t_stop,  t)

            # FIXME: this should be phased out
            if event[ru.EVENT] in 'advance':
                event[ru.EVENT] = 'state'

            if event[ru.EVENT] == 'state':
                state = event[ru.STATE]
                self._states[state] = event

            # we also treat state transitions as generic event.
            # Because, why not?
            self._events.append(event)

        if profile:
            self._ttc = self._t_stop - self._t_start

        # FIXME: assert state model adherence here (if state model is defined)


    # --------------------------------------------------------------------------
    #
    def _ensure_tuplelist(self, events):

        if not events:
            return []

        ret = list()
        if not isinstance(events, list):
            events = [events]

        for e in events:
            if isinstance(e,dict):
                et = ru.PROF_KEY_MAX * [None]
                for k,v in list(e.items()):
                    et[k] = v
                ret.append(tuple(et))
            else:
                ret.append(e)

        return ret


    # --------------------------------------------------------------------------
    #
    def as_dict(self):

        return {
                'uid'        : self._uid,
                'etype'      : self._etype,
                'states'     : self._states,
                'events'     : self._events,
                'cfg'        : self._cfg,
                'description': self._description,
               }


    # --------------------------------------------------------------------------
    #
    def dump(self):

        pprint.pprint(self.as_dict())


    # --------------------------------------------------------------------------
    #
    def list_states(self):

        return list(self._states.keys())


    # --------------------------------------------------------------------------
    #
    def duration(self, state=None, event=None, time=None, ranges=None):
        """
        This method accepts a set of initial and final conditions, interprets
        them as documented in the `ranges()` method (which has the same
        signature), and then returns the difference between the resulting
        timestamps.
        """

        if not ranges:
            ranges = self.ranges(state, event, time)
          # print 'get %5d ranges for %s' % (len(ranges), self.uid)
          # pprint.pprint(self.events)

        else:
            assert(not state)
            assert(not event)
            assert(not time)

            # make sure the ranges are collapsed (although they likely are
            # already...)
          # print 'use %5d ranges for %s' % (len(ranges), self.uid)
            ranges = ru.collapse_ranges(ranges)

        if not ranges:
            raise ValueError('no duration defined for given constraints '
                  '(%s) (%s) (%s) (%s)' % (state, event, time, ranges))

        return sum(r[1] - r[0] for r in ranges)


    # --------------------------------------------------------------------------
    #
    def timestamps(self, state=None, event=None, time=None):
        """
        This method accepts a set of conditions, and returns the list of
        timestamps for which those conditions applied, i.e., for which state
        transitions or events are known which match the given 'state' or 'event'
        parameter.  If no match is found, an empty list is returned.

        Both `state` and `event` can be lists, in which case the union of all
        timestamps are returned.

        The `time` parameter is expected to be a single tuple, or a list of
        tuples, each defining a pair of start and end time which are used to
        constrain the matching timestamps.

        The returned list will be sorted.
        """

        event = self._ensure_tuplelist(event)
        state = ru.as_list(state)
        ret   = list()

        if not event and not state:
            # no filters, consider all events
            ret = self._events

        for e in event:
            for x in self._events:
                if self._match_event(e,x):
                    ret.append(x[ru.TIME])

        for s in state:
            if s in self._states:
                ret.append(self._states[s][ru.TIME])

        # apply time filters
        if time:
            matched = list()
            for etime in ret:
                for ttuple in time:
                    if etime >= ttuple[0] and etime <= etime[1]:
                        matched.append(etime)
                        break
            ret = matched

        return sorted(ret)


    # --------------------------------------------------------------------------
    #
    def _match_event(self, needle, hay):

        for key in range(ru.PROF_KEY_MAX - 2):
            if needle[key] is not None:
                if key == ru.MSG:
                    if needle[key] not in hay[key]:
                        return False
                else:
                    if needle[key] != hay[key]:
                        return False
        return True


    # --------------------------------------------------------------------------
    #
    def ranges(self, state=None, event=None, time=None,
                     expand=False, collapse=True):
        """
        This method accepts a set of initial and final conditions, in the form
        of range of state and or event specifiers::

          entity.ranges(state=[['INITIAL_STATE_1', 'INITIAL_STATE_2'],
                                'FINAL_STATE_1',   'FINAL_STATE_2'  ]],
                        event=[[ initial_event_1,   initial_event_2 ]
                               [ final_event_1,     final_event_2   ]],
                        time =[[2.0, 2.5], [3.0, 3.5]])

        More specifically, the `state` and `event` parameter are expected to be
        a tuple, where the first element defines the initial condition, and the
        second element defines the final condition.  The `time` parameter is
        expected to be a single tuple, or a list of tuples, each defining a pair
        of start and end time which are used to constrain the resulting ranges.
        States are expected as strings, events as full event tuples::

            [ru.TIME,  ru.NAME, ru.UID,  ru.STATE, ru.EVENT, ru.MSG,  ru.ENTITY]

        where empty fields are not applied in the filtering - all other fields
        must match exactly.  The events can also be specified as dictionaries,
        which then don't need to have all fields set.

        The method will:

          - determine the *earliest* timestamp when any of the given initial
            conditions have been met, which can be either an event or a state;
          - determine the *next* timestamp when any of the given final
            conditions have been met (when `expand` is set to `False` [default])
            OR
          - determine the *last* timestamp when any of the given final
            conditions have been met (when `expand` is set to `True`)

        From that final point in time the search for the next initial condition
        applies again, which may result in another time range to be found.  The
        method returns the set of found ranges, as a list of `[start, end]` time
        tuples.

        The resulting ranges are constrained by the `time` constraints, if such
        are given.

        Note that with `expand=True`, at most one range will be found.

        Setting 'collapse' to 'True' (default) will prompt the method to
        collapse the resulting set of ranges.

        The returned ranges are time-sorted

        Example::

           unit.ranges(state=[rp.NEW, rp.FINAL]))
           unit.ranges(event=[{ru.NAME : 'exec_start'},
                              {ru.NAME : 'exec_ok'}])
        """

        # NOTE: this method relies on all state changes (as events in
        #       `self.states`) to also be recorded as events (as events in in
        #       `self.events` with `ru.NAME == 'state'`).

        if not state and not event:
            raise ValueError('duration needs state and/or event arguments')

        event = self._ensure_tuplelist(event)

        if not state: state = [[], []]
        if not event: event = [[], []]

        s_init  = state[0]
        s_final = state[1]
        e_init  = event[0]
        e_final = event[1]

        if not isinstance(s_init,  list): s_init  = [s_init ]
        if not isinstance(s_final, list): s_final = [s_final]
        if not isinstance(e_init,  list): e_init  = [e_init ]
        if not isinstance(e_final, list): e_final = [e_final]

        conds_init  = list()
        conds_final = list()

        for s in s_init:
            et = ru.PROF_KEY_MAX * [None]
            et[ru.STATE] = s
            et[ru.EVENT] = 'state'
            conds_init.append(tuple(et))

        for s in s_final:
            et = ru.PROF_KEY_MAX * [None]
            et[ru.STATE] = s
            et[ru.EVENT] = 'state'
            conds_final.append(tuple(et))

        for e in e_init:
            if isinstance(e,dict):
                et = ru.PROF_KEY_MAX * [None]
                for k,v in list(e.items()):
                    et[k] = v
                conds_init.append(tuple(et))
            else:
                conds_init.append(e)

      # t_start = sys.float_info.max
      # for e in e_init:
      #     for e_info in self._events:
      #         if self._match_event(e, e_info):
      #             t_start = min(t_start, e_info[ru.TIME])
      #
      # t_stop  = sys.float_info.min
      # for e in e_final:
      #     for e_info in self._events:
      #         if self._match_event(e, e_info):
      #             t_stop = max(t_stop, e_info[ru.TIME])
      #
      # if t_start == sys.float_info.max:
      #   # return []
      #     raise ValueError('initial condition did not apply')
      #
      # if t_stop == sys.float_info.min:
      #   # return []
      #     raise ValueError('final condition did not apply')
      #
      # if t_stop < t_start:
      #   # return []
      #     raise ValueError('duration uncovered time inconsistency')


        for e in e_final:
            if isinstance(e,dict):
                et = ru.PROF_KEY_MAX * [None]
                for k,v in list(e.items()):
                    et[k] = v
                conds_final.append(tuple(et))
            else:
                conds_final.append(e)

        ranges     = list()
        this_range = [None, None]

        # NOTE: this assumes that `self.events` are time sorted
        for e in self._events:
            if this_range[0] is None:
                # check for an initial event.
                for c in conds_init:
                    if self._match_event(c, e):
                        this_range[0] = e[ru.TIME]
                        break
            else:
                # check for a final event.  If found and '!expand`, then store
                # the now completed event away, and start a new one; if
                # `expand`, then keep searching for a later final event
                for c in conds_final:
                    if self._match_event(c, e):
                        this_range[1] = e[ru.TIME]
                        if not expand:
                            ranges.append(this_range)
                            this_range = [None, None]
                            break

        # we went through all events.  `this_range` may or may not be a usable
        # range here.  If it is, append it to ranges.
        if  this_range[0] is not None and \
            this_range[1] is not None     :
            ranges.append(this_range)

        # apply time filter, if specified
        # For all ranges, check if they fall completely or partially within any
        # of the given time filters.  If not, drop that range, if yes, include
        # the overlapping part.
        if not time or not len(time):
            ret = ranges

        else:
            ret = list()
            if not isinstance(time[0], list):
                time = [time]

            # for each range in ret, we make  sure that it does not violate any
            # time filter
            for erange in ranges:
                for trange in time:
                    new_start = max(trange[0], erange[0])
                    new_stop  = min(trange[1], erange[1])
                    if new_stop > new_start:
                        ret.append([new_start, new_stop])

        if collapse:
            ret = ru.collapse_ranges(ret)

        return sorted(ret)


# ------------------------------------------------------------------------------

