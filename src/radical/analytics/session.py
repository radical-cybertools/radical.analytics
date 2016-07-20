

import radical.utils as ru

from .entity import Entity


# ------------------------------------------------------------------------------
#
class Session(object):

    def __init__(self, profile, description, _entities=None):

        # we can't do any analysis on empty profile
        assert(profile)

        self._profile     = profile
        self._description = description

        # internal state is represented by a dict of entities:
        # dict keys are entity uids (which are assumed to be unique per
        # session), dict values are ra.Entity instances
        # if `_entities` are given, we don't need to initialize them
        if _entities is not None:
            self._entities = _entities
        else:
            self._entities = dict()
            self._initialize_entities()

        # we do some bookkeeping in self._properties where we keep a list of
        # property values around which we encountered in self._entities.
        self._properties = dict()
        self._initialize_properties()

        # FIXME: we should do a sanity check that all encountered states and
        #        events are part of the respective state and event models


    # --------------------------------------------------------------------------
    #
    def _initialize_entities(self):
        """
        populate self._entities from self._profile and 
        self._description.

        NOTE: We derive entity types via some heuristics for now: we assume the
        first part of any dot-separated uid to signify an entity type.
        """

        # this method can only be called once
        assert (not self._entities)

        # create entities from the profile events: 
        entity_events  = dict()

        for event in self._profile:
            uid = event['uid']
            if uid not in entity_events:
                entity_events[uid] = list()
            entity_events[uid].append(event)

        # for all uids found,  create and store an entity.  We look up the
        # entity type in one of the events (and assume it is consistent over 
        # all events for that uid)
        for uid,events in entity_events.iteritems():
            etype = events[0]['entity_type']
            self._entities[uid] = Entity(_uid=uid, 
                                         _etype=etype, 
                                         _profile=events)


    # --------------------------------------------------------------------------
    #
    def _initialize_properties(self):
        """
        populate self._properties from self._entities.  Self._properties has the
        following format:

            {
              'state' : {
                'NEW'      : 10,
                'RUNNING'  :  8,
                'DONE      :  7,
                'FAILED'   :  1,
                'CANCELED' :  2
              }
            }

        So we basically count how often any property value appears in the
        current set of entities.

        RA knows exactly 4 properties:
          - uid   (entity idetifiers)
          - etype (type of entities)
          - event (names of events)
          - state (state identifiers)
        """

        # FIXME: initializing properties can be expensive, and we might not
        #        always need them anyway.  So we can lazily defer this 
        #        initialization stop until the first query which requires them.

        # we do *not* look at profile and descriptions anymore, those are only
        # evaluated once on construction, in `_initialize_entities()`.  Now we
        # don't parse all that stuff again, but only re-initialize after
        # in-place filtering etc.
        self._properties = { 'uid'   : dict(),
                             'etype' : dict(),
                             'event' : dict(),
                             'state' : dict()}

        for euid,e in self._entities.iteritems():

            if euid in self._properties['uid']:
                raise RuntimeError('duplicated uid %s' % euid)
            self._properties['uid'][euid] = 1

            if e.etype not in self._properties['etype']:
                self._properties['etype'][e.etype] = 0
            self._properties['etype'][e.etype] += 1

            for state in e.states:
                if state not in self._properties['state']:
                    self._properties['state'][state] = 0
                self._properties['state'][state] += 1

            for event in e.events:
                if event not in self._properties['event']:
                    self._properties['event'][event] = 0
                self._properties['event'][event] += 1


    # --------------------------------------------------------------------------
    #
    def _apply_filter(self, etype=None, uid=None, state=None, 
                            event=None, time=None):

        # iterate through all self._entities and collect UIDs of all entities
        # which match the given set of filters (after removing all events which
        # are not in the given time ranges)
        if not etype: etype = []
        if not uid  : uid   = []
        if not state: state = []
        if not event: event = []
        if not time : time  = []

        if etype and not isinstance(etype, list): etype = [etype]
        if uid   and not isinstance(uid  , list): uid   = [uid  ]
        if state and not isinstance(state, list): state = [state]
        if event and not isinstance(event, list): event = [event]

        if time and len(time) and not isinstance(time[0], list): time = [time]

        ret = list()
        for eid,entity in self._entities.iteritems():

            if etype and entity.etype not in etype: continue
            if uid   and entity.uid   not in uid  : continue
            
            if state:
                match = False
                for s,sdict in entity.states.iteritems():
                    if time and not ru.in_range(sdict['time'], time):
                        continue
                    if s in state:
                        match = True
                        break
                if not match:
                     continue

            if event:
                match = False
                for e,edict in entity.events.iteritems():
                    if time and not ru.in_range(edict['time'], time):
                        continue
                    if e in event:
                        match = True
                        break
                if not match:
                     continue

            # all existing filters have been passed - this is a match!
            ret.append(eid)

        return ret


    # --------------------------------------------------------------------------
    #
    def _dump(self):

        for uid,entity in self._entities.iteritems():
            print "\n\n === %s" % uid
            entity.dump()
            for event in entity.events:
                print "  = %s" % event
                for e in entity.events[event]:
                    print "    %s" % e


    # --------------------------------------------------------------------------
    #
    def list(self, pname=None):

        if not pname:
            # return the name of all known properties
            return self._properties.keys()

        if isinstance(pname, list):
            return_list = True
            pnames = pname
        else:
            return_list = False
            pnames = [pname]

        ret = list()
        for _pname in pnames:
            if _pname not in self._properties:
                raise KeyError('no such property known (%s) / %s' \
                        % (_pname, self._properties.keys()))
            ret.append(self._properties[_pname].keys())

        if return_list: return ret
        else          : return ret[0]


    # --------------------------------------------------------------------------
    #
    def get(self, etype=None, uid=None, state=None, event=None, time=None):

        uids = self._apply_filter(etype=etype, uid=uid, state=state,
                                  event=event, time=time)
        return [self._entities[uid] for uid in uids]


    # --------------------------------------------------------------------------
    #
    def filter(self, etype=None, uid=None, state=None, event=None, time=None, 
               inplace=True):

        uids = self._apply_filter(etype=etype, uid=uid, state=state,
                                  event=event, time=time)

        if inplace:
            # filter our own entity list, and refresh the properties based on
            # the new list
            if uids != self._entities.keys():
                self._entities = {uid:self._entities[uid] for uid in uids}
                self._initialize_properties()
            return self

        else:
            # create a new session with the resulting property list
            entities = {uid:self._entities[uid] for uid in uids}
            return Session(profile     = self._profile,
                           description = self._description, 
                           _entities   = entities)


    # --------------------------------------------------------------------------
    #
    def describe(self, mode=None, etype=None):

        if mode not in [None, 'state_model', 'event_model']:
            raise ValueError('describe parameter "mode" invalid')

        if not etype:
            # no entity filter applied: return the full description
            return self._description

        if not isinstance(etype,list):
            etype = [etype]

        ret = dict()
        for et in etype:
            if et in self._description['entities']:
                state_model = self._description['entities'][et]['state_model']
                event_model = self._description['entities'][et]['event_model']
                        
            else:
                # we don't have any state or event model -- return minimalistic
                # ones
                state_model = {'ALIVE' : 0},
                event_model = {}

            if not mode:
                ret[et] = {'state_model' : state_model,
                           'event_model' : event_model}

            elif mode == 'state_model':
                ret[et] = {'state_model' : state_model}

            elif mode == 'event_model':
                ret[et] = {'event_model' : event_model}

        return ret


    # --------------------------------------------------------------------------
    #
    def range(self, state=None, event=None, time=None):
        """
        This method accepts a set of initial and final conditions, in the form
        of range of state and or event specifiers:

          entity.range(state=[['INITIAL_STATE_1', 'INITIAL_STATE_2'], 
                               'FINAL_STATE_1',   'FINAL_STATE_2']], 
                       event=['initial_event_1',  'final_event'],
                       time =[[2.0, 2.5], [3.0, 3.5]])

        More specifically, the `state` and `event` parameter are expected to be
        a tuple, where the first element defines the initial condition, and the
        second element defines the final condition. Each element can be a string
        or a list of strings.  The `time` parameter is expected to be a single
        tuple, or a list of tuples, each defining a pair of start and end time
        which are used to constrain the resulting ranges.

        The parameters are interpreted as follows: 

          - for any entity known to the session
            - determine the maximum time range during which the entity has been
              between initial and final conditions

          - collapse the resulting set of ranges into the smallest possible set
            of ranges which cover the same, but not more nor less, of the
            domain (floats).

          - limit the resulting ranges by the `time` constraints, if such are
            given.


        Example:

           session.range(state=[rp.NEW, rp.FINAL]))

        where `rp.FINAL` is a list of final unit states.
        """

        ranges = list()
        for uid,entity in self._entities.iteritems():
            ranges += entity.range(state, event, time)

        return ru.collapse_ranges(ranges)


    # --------------------------------------------------------------------------
    #
    def duration(self, state=None, event=None, time=None):
        """
        This method accepts the same set of parameters as the `range()` method,
        and will use the range method to obtain a set of ranges.  It will return
        the sum of the durations for all resulting ranges.

        Example:

           session.duration(state=[rp.NEW, rp.FINAL]))

        where `rp.FINAL` is a list of final unit states.
        """

        ret    = 0.0
        ranges = self.range(state, event, time)
        for range in ranges:
            ret += range[1] - range[0]

        return ret


    # --------------------------------------------------------------------------
    #
    def concurrency(self, state=None, event=None, time=None):
        """
        This method accepts the same set of parameters as the `range()` method,
        and will use the range method to obtain a set of ranges.  It will return
        a time series, counting the number of units which are concurrently
        matching the range filter at any point in time.  The descrete points in
        time for which the concurrency is computed are all points at which the
        concurrency changes.

        Returned is an ordered list of tuples:

          [ [time_0, concurrency_0] ,
            [time_1, concurrency_1] ,
            ...
            [time_n, concurrency_n] ]

        where `time_n` is represented s `float`, and `concurrency_n` as `int`.

        Example:

           session.concurrency(state=[rp.EXECUTING, 
                                      rp.AGENT_STAGING_OUTPUT_PENDING]))

        """

        ret    = 0.0
        ranges = self.range(state, event, time)
        for range in ranges:
            ret += range[1] - range[0]

        return ret


# ------------------------------------------------------------------------------

