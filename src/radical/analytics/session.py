
from .entity import Entity


# ------------------------------------------------------------------------------
#
class Session(object):

    def __init__(self, profiles, description, _entities=None):

        # we can't do any analysis on empty profiles
        assert(profiles)

        self._profiles    = profiles
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


    # --------------------------------------------------------------------------
    #
    def _initialize_entities(self):
        """
        populate self._entities from self._profiles and 
        self._description.

        NOTE: We derive entity types via some heuristics for now: we assume the
        first part of any dot-separated uid to signify an entity type.
        """

        # this method can only be called once
        assert (not self._entities)

        # create entities from the profile events: 
        entity_events  = dict()

        for event in self._profiles:
            uid = event['uid']
            if uid not in entity_events:
                entity_events[uid] = list()
            entity_events[uid].append(event)

        # for all uids found,  create and store an entity.  We look up the
        # entity type in one of the events (and assume it is consistent over 
        # all events for that uid)
        for uid,events in entity_events.iteritems():
            print len(events)
            print events[0]
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
        """
        # we do *not* look at profiles and descriptions anymore, those are only
        # evaluated once on construction, in `_initialize_entities()`.  Now we
        # don't parse all that stuff again, but only re-initialize after
        # in-place filtering etc.
        #
        # TODO: we have no means to get the counters, yet.
        pass


    # --------------------------------------------------------------------------
    #
    def _apply_filter(entities=None, uids=None, states=None, events=None):

        # iterate through all self._entities and collect UIDs of all entities
        # which match the given set of filters
        if entities and not isinstance(entities, list): entities = [entities]
        if uids     and not isinstance(uids    , list): uids     = [uids    ]
        if states   and not isinstance(states  , list): states   = [states  ]
        if events   and not isinstance(events  , list): events   = [events  ]

        uids = list()
        for e in self._entities:

            if entities and e.entity not in entities: continue
            if uids     and e.uid      not in uids    : continue
            if states   and e.states   not in states  : continue
            if events   and e.event    not in events  : continue
            # FIXME: above is wrong as e.states and e.events are lists.  We need
            #        to intersect those lists with the filter, and continue on
            #        any empty intersection.

            # all existing filters have been passed - this is a match!
            uids.append(e.uid)

        return uids


    # --------------------------------------------------------------------------
    #
    def dump(self):

        for uid,entity in self._entities.iteritems():
            print "\n\n === %s" % uid
            entity.dump()
            for ename in entity.events:
                print "  = %s" % ename
                for e in entity.events[ename]:
                    print "    %s" % e


    # --------------------------------------------------------------------------
    #
    def list(self, property_name=None):

        if not property_name:
            # return the name of all known properties
            return self._properties.keys()

        if propery_name not in self._properties:
            raise KeyError('no such property known')

        return self._properties[property_name]


    # --------------------------------------------------------------------------
    #
    def get(self, entities=None, uids=None, states=None, events=None):

        uids = self._apply_filter(entities, uids, states, events)
        return [self._entities[uid] for uid in uids]


    # --------------------------------------------------------------------------
    #
    def filter(self, entities=None, uids=None, states=None, events=None,
            inplace=True):

        uids = self._apply_filter(entities, uids, states, events)

        if inplace:
            # filter our own entity list, and refresh the properties based on
            # the new list
            if uids != self._entities.keys():
                self._entities = [self._entities[uid] for uid in uids]
                self._initialize_properties()

        else:
            # create a new session with the resulting property list
            entities = [self._entities[uid] for uid in uids]
            return Session(profiles    = self._profiles,
                           description = self._description, 
                           _entities   = entities)





    # --------------------------------------------------------------------------
    #
    def describe(entities=None):

        if not entities:
            # no entity filter applied: return the full description
            return self._description

        if not isinstance(entities,list):
            entities = [entities]

        ret = dict()
        for entity in entities:
            ret[entity] = {
                    'state_model' : self._description['entities'][entity]['state_model'],
                    'event_model' : self._description['entities'][entity]['event_model']}
        return ret


    # --------------------------------------------------------------------------
    #
    def duration(self, start_states=None, end_states=None, 
                       start_events=None, end_events=None):

        if not start_states and not start_events:
            raise ValueError('duration needs either start_states or start_events')

        if not end_states and not end_events:
            raise ValueError('duration needs either end_states or end_events')

        if start_states and not end_states:
            raise ValueError('duration needs start_states and end_states')

        if start_events and not end_events:
            raise ValueError('duration needs start_events and end_events')

        if start_states and end_states:
            # magic goes here
            pass

        elif start_events and end_events:
            # magic goes here
            pass


# ------------------------------------------------------------------------------

