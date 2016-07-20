

import sys

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

        self._t_start     = None
        self._t_stop      = None
        self._ttc         = None

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
        entity_events = dict()

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

        if self._entities:
            self._t_start = sys.float_info.max
            self._t_stop  = sys.float_info.min

        for euid,e in self._entities.iteritems():

            self._t_start = min(self._t_start, e.t_start)
            self._t_stop  = max(self._t_stop,  e.t_stop )

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


        if self._entities:
            self._ttc = self._t_stop - self._t_start


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

        if mode not in [None, 'state_model', 'state_values', 'event_model']:
            raise ValueError('describe parameter "mode" invalid')

        if not etype:
            # no entity filter applied: return the full description
            return self._description

        if not isinstance(etype,list):
            etype = [etype]

        ret = dict()
        for et in etype:
            if et in self._description['entities']:
                state_model  = self._description['entities'][et]['state_model']
                state_values = self._description['entities'][et]['state_values']
                event_model  = self._description['entities'][et]['event_model']
                        
            else:
                # we don't have any state or event model -- return minimalistic
                # ones
                state_model  = {'ALIVE' : 0},
                state_values = {0 : 'ALIVE'},
                event_model  = {}

            if not mode:
                ret[et] = {'state_model'  : state_model,
                           'state_values' : state_values, 
                           'event_model'  : event_model}

            elif mode == 'state_model':
                ret[et] = {'state_model'  : state_model}

            elif mode == 'state_values':
                ret[et] = {'state_values' : state_values}

            elif mode == 'event_model':
                ret[et] = {'event_model'  : event_model}

        return ret


    # --------------------------------------------------------------------------
    #
    def ranges(self, state=None, event=None, time=None):
        """
        This method accepts a set of initial and final conditions, in the form
        of range of state and or event specifiers:

          entity.ranges(state=[['INITIAL_STATE_1', 'INITIAL_STATE_2'], 
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

           session.ranges(state=[rp.NEW, rp.FINAL]))

        where `rp.FINAL` is a list of final unit states.
        """

        ranges = list()
        for uid,entity in self._entities.iteritems():
            ranges += entity.ranges(state, event, time)

        return ru.collapse_ranges(ranges)


    # --------------------------------------------------------------------------
    #
    def duration(self, state=None, event=None, time=None):
        """
        This method accepts the same set of parameters as the `ranges()` method,
        and will use the `ranges()` method to obtain a set of ranges.  It will
        return the sum of the durations for all resulting ranges.

        Example:

           session.duration(state=[rp.NEW, rp.FINAL]))

        where `rp.FINAL` is a list of final unit states.
        """

        ret    = 0.0
        ranges = self.ranges(state, event, time)
        for r in ranges:
            ret += r[1] - r[0]

        return ret


    # --------------------------------------------------------------------------
    #
    def concurrency(self, state=None, event=None, time=None, sampling=None):
        """
        This method accepts the same set of parameters as the `ranges()` method,
        and will use the `ranges()` method to obtain a set of ranges.  It will
        return a time series, counting the number of units which are
        concurrently matching the ranges filter at any point in time.  
        
        The additional parameter `smpling` determines the exact points in time
        for which the concurrency is computed, and thus determines the sampling
        rate for the returned time series.  If not specified, the time series
        will contain all points at which the concurrency changed.  If specified,
        it is interpreted as second (float) interval at which, after the
        starting point (begin of first event matching the filters) the
        concurrency is computed.

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

        ranges = list()
        for uid,e in self._entities.iteritems():
            ranges += e.ranges(state, event, time)

        if not ranges:
            # nothing to do
            return []


        ret   = list()
        times = list()
        if sampling:
            # get min and max of ranges, and add create timestamps at regular
            # intervals
            r_min = ranges[0][0]
            r_max = ranges[0][1]
            for r in ranges:
                r_min = min(r_min, r[0])
                r_max = max(r_max, r[1])

            t = r_min
            while t < r_max:
                times.append(t)
                t += sampling
            times.append(t)

        else:
            # get all start and end times for all ranges, and use the resulting
            # set as time sequence
            for r in ranges:
                times.append(r[0])
                times.append(r[1])
            times.sort()

        # we have the time sequence, now compute concurrency at those points
        for t in times:
            cnt = 0
            for r in ranges:
                if t >= r[0] and t <= r[1]:
                    cnt += 1
            
            ret.append([t, cnt])

        return ret


# ------------------------------------------------------------------------------

