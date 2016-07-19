
# ------------------------------------------------------------------------------
#
class Entity(object):

    def __init__(self, _uid, _ename, _profile):
        """
        This is a private constructor for an RA Entity: it gets a series of
        events and sorts it into its properties.  We have 4 properties:

          - ename : the type of the entity in question.  This defines, amongst
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
        self._ename      = _ename
        self._states     = dict()
        self._events     = dict()

        self._initialize(_profile)


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
                'ename'  : self._ename, 
                'states' : self._states, 
              # 'events' : self._events
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
    def ename(self):
        return self._ename

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
    def duration(self):

        # FIXME
        return 0.0


# ------------------------------------------------------------------------------

