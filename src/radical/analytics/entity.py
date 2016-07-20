
import sys


# ------------------------------------------------------------------------------
#
class Entity(object):

    def __init__(self, _uid, _etype, _profile):
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
        assert(_profile)

        self._uid        = _uid
        self._etype      = _etype
        self._states     = dict()
        self._events     = dict()

        self._initialize(_profile)


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

        # we expect each event to have `time` and `name`, and expect events
        # named 'state' to signify a state transition, and thus to always have
        # the property 'state' set, too
        for event in profile:

            assert('time' in event)

            name = event['event_name']
            if name == 'state':
                state = event['state']
                self._states[state] = event

            # we also treat state transitions as generic event.
            # Because, why not?
            if name not in self._events:
                self._events[name] = list()
            self._events[name].append(event)

        # FIXME: assert state model adherence here
        # FIXME: where to get state model from?


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
    def events(self):
        return self._events


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
    def duration(self, state=None, event=None):
        """
        This method accepts a set of initial and final conditions, interprets
        them as documented in the `range()` method (which has the same
        signature), and then returns the difference between the resulting
        timestamps.
        """
        t_start, t_stop = self.range(state, event)

        return t_stop - t_start


    # --------------------------------------------------------------------------
    #
    def range(self, state=None, event=None):
        """
        This method accepts a set of initial and final conditions, in the form
        of range of state and or event specifiers:

          entity.range(state=[['INITIAL_STATE_1', 'INITIAL_STATE_2'],
                               'FINAL_STATE_1',   'FINAL_STATE_2']],
                       event=['initial_event_1', 'final_event'])

        More specifically, the `state` and `event` parameter are expected to be
        a tuple, where the first element defines the initial condition, and the
        second element defines the final condition. Each element can be a string
        or a list of strings.

        The parameters are interpreted as follows: the method will

          - determine the *earliest* timestamp when any of the given initial
            conditions have been met (`t_start`);
          - determine the *latest* timestamp when any of the given final
            conditions have been met (`t_stop`);
          - return the tuple `[t_stop, t_start]`

        Example:

           unit.range(state=[rp.NEW, rp.FINAL]))

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
            raise ValueError('initial condition did not apply')

        if t_stop == sys.float_info.min:
            raise ValueError('final condition did not apply')

        if t_stop < t_start:
            raise ValueError('duration uncovered time inconsistency')

        return [t_start, t_stop]


# ------------------------------------------------------------------------------

