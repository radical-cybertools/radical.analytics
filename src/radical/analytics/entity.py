
import os
import sys

import radical.pilot as rp


# ------------------------------------------------------------------------------
#
class Entity(object):

    def __init__(self, _uid, _etype, _profile, _details):
        """
        This is a private constructor for an RA Entity: it gets a series of
        events and sorts it into its properties.  We have 4 properties:

          - etype : the type of the entity in question.  This defines, amongst
                    others, what state model the Session will assume to be valid
                    for this entity
          - uid   : an ID assumed to be unique in the scope of an RA Session
          - states: a set of timed state transitions which are assumed to adhere
                    to a well defined state model
          - events: a time series of named, but otherwise unspecified events
        """

        assert(_uid)
      # assert(_profile)

        self._uid         = _uid
        self._etype       = _etype
        self._details     = _details
        self._description = self._details.get('description', dict())
        self._cfg         = self._details.get('cfg',         dict())

        # FIXME: this should be sorted out on RP level
        self._cfg['hostid'] = self._details['hostid']

        self._states      = dict()
        self._events      = dict()
        self._consistency = { 'log'         : list(), 
                              'state_model' : None, 
                              'event_model' : None, 
                              'timestamps'  : None}

        self._t_start     = None
        self._t_stop      = None
        self._ttc         = None

        self._initialize(_profile)


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

        return "ra.Entity [%s]: %s\n    states: %s\n    events: %s" \
                % (self.etype, self.uid,
                   self._states.keys(), self._events.keys())


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

        self._t_start = sys.float_info.max
        self._t_stop  = sys.float_info.min

      # if self.uid == os.environ.get('FILTER'):
      #     print '\n\n%s' % self.uid

        # we expect each event to have `time` and `event_type`, and expect
        # 'state' events to signify a state transition, and thus to always 
        # have the property 'state' set, too
        for event in sorted(profile, key=lambda (x): (x['time'])):

          # if self.uid == os.environ.get('FILTER'):
          #     if 'Listen' not in event['msg']:
          #         print event

            t = event['time']

            self._t_start = min(self._t_start, t)
            self._t_stop  = max(self._t_stop,  t)

            etype = event['event_type']
            if etype == 'state':
                state = event['state']
              # if self.uid == os.environ.get('FILTER'):
              #     print '%s  %-25s  %8.2f' % (self.uid, state, event['time'])
              #     print event
                self._states[state] = event

            # we also treat state transitions as generic event.
            # Because, why not?
            if etype not in self._events:
                self._events[etype] = list()
            self._events[etype].append(event)

        # FIXME: assert state model adherence here
        # FIXME: where to get state model from?
        # FIXME: sort events by time

        # for pilots, we may not have any states.  If thst is the case, we dig
        # them out of the state hostory
        #
        # FIXME: the fallback to state history will not make sense for current
        #        RP profiles anymore, and should be removed before release.  It
        #        does not change the data though.
        #
        statehist = self._details.get('json', {}).get('statehistory', [])
        for e in statehist:
            if e['state'] not in self._states:
                self._states[e['state']] = {
                        'entity_type' : self._etype,
                        'event_type'  : 'state', 
                        'msg'         : e['state'],
                        'name'        : '', 
                        'time'        : float(e['timestamp']) - float(self._details['t_min']),
                        'uid'         : self._uid
                        }

                t = float(e['timestamp'])
                self._t_start = min(self._t_start, t)
                self._t_stop  = max(self._t_stop,  t)


        # if we don't have a final state, we assume last entry as FAILED
        if  rp.DONE     not in self._states and \
            rp.FAILED   not in self._states and \
            rp.CANCELED not in self._states :
            if not profile:
                self._states[rp.FAILED] = {
                        'entity_type' : self._etype,
                        'event_type'  : 'state',
                        'msg'         : rp.FAILED,
                        'name'        : '', 
                        'time'        : self._details['t_max'],
                        'uid'         : self._uid
                        }
            else:
                self._states[rp.FAILED] = {
                        'entity_type' : self._etype,
                        'event_type'  : 'state',
                        'msg'         : rp.FAILED,
                        'name'        : '', 
                        'time'        : profile[-1]['time'],
                        'uid'         : self._uid
                        }

        self._ttc = self._t_stop - self._t_start



    # --------------------------------------------------------------------------
    #
    def as_dict(self):

        return {
                'uid'    : self._uid,
                'etype'  : self._etype,
                'states' : self._states,
                'events' : self._events
               }


    # --------------------------------------------------------------------------
    #
    def dump(self):

        import pprint
        pprint.pprint(self.as_dict())


    # --------------------------------------------------------------------------
    #
    def list_states(self):

        return self._states.keys()


    # --------------------------------------------------------------------------
    #
    def list_events(self):

        return self._events.keys()


    # --------------------------------------------------------------------------
    #
    def duration(self, state=None, event=None, time=None):
        """
        This method accepts a set of initial and final conditions, interprets
        them as documented in the `ranges()` method (which has the same
        signature), and then returns the difference between the resulting
        timestamps.
        """
        ranges = self.ranges(state, event, time)

        if not ranges:
            return None
          # raise ValueError('no duration defined for given constraints')

        ret = 0.0
        for r in ranges:
            ret += r[1] - r[0]

        return ret


    # --------------------------------------------------------------------------
    #
    def timestamps(self, state=None, event=None):
        """
        This method accepts a set of conditions, and returns the list of
        timestamps for which those conditions applied, i.e. for which state
        transitions or events are known which match the given 'state' or 'event'
        parameter.  If no match is found, an empty list is returned.

        Both `state` and `event` can be lists, in which case the union of all
        timestamps are returned.

        The returned list will be sorted.
        """

        if not event:
            event = []
        elif not isinstance(event, list):
            event = [event]

        if not state:
            state = []
        elif not isinstance(state, list):
            state = [state]
        
        ret = []

        for e in event:
            for x in self._events.get(e, []):
                ret.append(x['time'])

        for s in state:
            if s in self._states:
                ret.append(self._states[s]['time'])

        return sorted(ret)


    # --------------------------------------------------------------------------
    #
    def ranges(self, state=None, event=None, time=None):
        """
        This method accepts a set of initial and final conditions, in the form
        of range of state and or event specifiers:

          entity.ranges(state=[['INITIAL_STATE_1', 'INITIAL_STATE_2'],
                                'FINAL_STATE_1',   'FINAL_STATE_2']],
                        event=['initial_event',  'final_event'],
                        time =[[2.0, 2.5], [3.0, 3.5]])

        More specifically, the `state` and `event` parameter are expected to be
        a tuple, where the first element defines the initial condition, and the
        second element defines the final condition. Each element can be a string
        or a list of strings.  The `time` parameter is expected to be a single
        tuple, or a list of tuples, each defining a pair of start and end time
        which are used to constrain the resulting ranges.

        The parameters are interpreted as follows: the method will

          - determine the *earliest* timestamp when any of the given initial
            conditions have been met (`t_start`);
          - determine the *latest* timestamp when any of the given final
            conditions have been met (`t_stop`);

          - limit the resulting range by the `time` constraints, if such are
            given.

          - return the resulting list of time tuples signifying the set of
            ranges where all constraints apply.

        Example:

           unit.ranges(state=[rp.NEW, rp.FINAL]))

        where `rp.FINAL` is a list of final unit states.
        """

        t_start = sys.float_info.max
        t_stop  = sys.float_info.min

        if not state and not event:
            raise ValueError('duration needs state and/or event arguments')

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


        for s in s_init:
            s_info = self._states.get(s)
            if s_info:
                t_start = min(t_start, s_info['time'])

        for s in s_final:
            s_info = self._states.get(s)
            if s_info:
                t_stop = max(t_stop, s_info['time'])


        for e in e_init:
            e_infos = self._events.get(e, [])
            for e_info in e_infos:
                t_start = min(t_start, e_info['time'])

        for e in e_final:
            e_infos = self._events.get(e, [])
            for e_info in e_infos:
                t_stop = max(t_stop, e_info['time'])


        if t_start == sys.float_info.max:
            return []
          # raise ValueError('initial condition did not apply')

        if t_stop == sys.float_info.min:
            return []
          # raise ValueError('final condition did not apply')

        accuracy = 0.1
        if t_start - t_stop > accuracy:
            raise ValueError('duration uncovered time inconsistency')

        # apply time filter, if such one is given
        ret = list()
        if time and len(time):

            # we actually inverse the logic here: we assume that all given time
            # filters are ranges to consider valid, but constrain them by the
            # one range we have determined by the state and event filter above.

            if not isinstance(time[0], list):
                time = [time]

            for trange in time:

                trange_start = trange[0]
                trange_stop  = trange[1]

                assert(trange_start <= trange_stop)

                if trange_start < t_start:
                    trange_start = t_start

                if trange_stop > t_stop:
                    trange_stop = t_stop

                if trange_start < trange_stop:
                    ret.append([trange_start, trange_stop])

        else:
            # no time filters defined
            ret.append([t_start, t_stop])

        return ret


# ------------------------------------------------------------------------------

