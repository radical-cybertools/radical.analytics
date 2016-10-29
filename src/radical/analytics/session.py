

import os
import sys
import copy

import radical.utils as ru

from .entity import Entity


# ------------------------------------------------------------------------------
#
class Session(object):

    def __init__(self, sid, stype, src=None, _entities=None, _init=True):
        """
        Create a radical.analytics session for analysis.

        The session is created from a set of profiles, which usually have been
        produced from some other session object in the RCT stack, such as
        radical.pilot.  The `ra.Session` constructor expects the respecive
        session ID and session type.  It optionally accepts a `src` parameter
        which can point to a location where the profiles are expected to be
        found, or where they will be stored after fetching them.  The default
        value for `src` is `$PWD/sid`.
        """

        self._sid   = sid
        self._stype = stype

        if not src:
            src = "%s/%s" % (os.getcwd(), sid)

        self._src = src

        if stype == 'radical.pilot':
            import radical.pilot as rp
            self._profile, self._t_min = rp.utils.get_session_profile    (sid=sid, src=self._src)
            self._description, hm      = rp.utils.get_session_description(sid=sid, src=self._src)

            self._description['accuracy'] = None
            self._description['hostmap']  = hm

        else:
            raise ValueError('unsupported session type [%s]' % stype)

        self._t_start     = None
        self._t_stop      = None
        self._ttc         = None

        self._log         = None

        # internal state is represented by a dict of entities:
        # dict keys are entity uids (which are assumed to be unique per
        # session), dict values are ra.Entity instances.
        self._entities = dict()
        if _init:
            self._initialize_entities()

        # we do some bookkeeping in self._properties where we keep a list of
        # property values around which we encountered in self._entities.
        self._properties = dict()
        if _init:
            self._initialize_properties()

        # FIXME: we should do a sanity check that all encountered states and
        #        events are part of the respective state and event models


    # --------------------------------------------------------------------------
    #
    def __deepcopy___(self, memo):

        cls = self.__class__
        ret = cls(sid=self._sid, stype=self._stype, _init=False)

        memo[id(self)] = ret

        for k, v in self.__dict__.items():
            setattr(ret, k, deepcopy(v, memo))

        return ret


    # --------------------------------------------------------------------------
    #
    def _reinit(self, entities):
        """
        After creating a session clone, we have identical sets of descriptions,
        profiles, and entities.  However, if we apply a filter during the clone
        creation, we end up with a deep copy which should have a *different* set
        of entities.  This method applies that new entity set to such a cloned
        session.
        """

        self._entities = entities

        # FIXME: we may want to filter the session description etc. wrt. to the
        #        entity types remaining after a filter.


    # --------------------------------------------------------------------------
    #
    @property
    def _rep(self):

        if not self._log:
            self._log = ru.get_logger('radical.analytics')

        return self._log.report


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
        # we also make sure that all pilots and units are represented, even if
        # they don't have a profile
        for uid in self._description['tree']:
            if uid in entity_events:
                events  = entity_events[uid]
                etype   = events[0]['entity_type']
                details = self._description['tree'][uid]
                details['hostid'] = self._description['hostmap'].get(uid)
                details['t_min']  = float(self._t_min)
                details['t_max']  = float(self._profile[-1]['time'])
            else:
                # no events, just json
                events  = list()
                etype   = uid.split('.')[0]
                details = self._description['tree'][uid]
                details['hostid'] = self._description['hostmap'].get(uid)
                details['t_min']  = float(self._t_min)
                details['t_max']  = float(self._profile[-1]['time'])

            self._entities[uid] = Entity(_uid=uid,
                                         _etype=etype,
                                         _profile=events, 
                                         _details=details)


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
            # filter our own entity list, and refresh the entity based on
            # the new list
            if uids != self._entities.keys():
                self._entities = {uid:self._entities[uid] for uid in uids}
                self._initialize_properties()
            return self

        else:
            # create a new session with the resulting entity list
            ret = Session(sid=self._sid, stype=self._stype, src=self._src,
                          _init=False)
            ret._reinit(entities = {uid:self._entities[uid] for uid in uids})
            ret._initialize_properties()
            return ret


    # --------------------------------------------------------------------------
    #
    def describe(self, mode=None, etype=None):

        if mode not in [None, 'state_model', 'state_values',
                              'event_model', 'relations']:
            raise ValueError('describe parameter "mode" invalid')

        if not etype and not mode:
            # no entity filter applied: return the full description
            return self._description

        if not etype:
            etype = self.list('etype')

        if not isinstance(etype,list):
            etype = [etype]

        ret = dict()
        for et in etype:

            state_model  = None
            state_values = None
            event_model  = None

            if et in self._description['entities']:
                state_model  = self._description['entities'][et]['state_model']
                state_values = self._description['entities'][et]['state_values']
                event_model  = self._description['entities'][et]['event_model']

            if not state_model  : state_model  = dict()
            if not state_values : state_values = dict()
            if not event_model  : event_model  = dict()

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

        if not mode or mode == 'relations':

           if len(etype) != 2:
               raise ValueError('relations expect an etype *tuple*')

           # we interpret the query as follows: for the two given etypes, walk
           # through the relationship tree and for all entities of etype[0]
           # return a list of all child entities of etype[1].  The result is
           # returned as a dict.

           parent_uids = self._apply_filter(etype=etype[0])
           child_uids  = self._apply_filter(etype=etype[1])

           rel = self._description['tree']
           for p in parent_uids:

               ret[p] = list()
               if p not in rel:
                   print 'inconsistent : no relations for %s' % p
                   continue

               for c in rel[p]['children']:
                   if c in child_uids:
                       ret[p].append(c)

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
            try:
                ranges += entity.ranges(state, event, time)
            except ValueError:
                # ignore entities for which the conditions did not apply
                pass

        if not ranges:
            raise ValueError('no duration defined for given constraints')

        return ru.collapse_ranges(ranges)


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

        ret = list()
        for uid,entity in self._entities.iteritems():
            ret += entity.timestamps(state=state, event=event)

        return sorted(ret)


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

        The additional parameter `sampling` determines the exact points in time
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

        where `time_n` is represented as `float`, and `concurrency_n` as `int`.

        Example:

           session.filter(etype='unit').concurrency(state=[rp.AGENT_EXECUTING,
                                        rp.AGENT_STAGING_OUTPUT_PENDING])
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


    # --------------------------------------------------------------------------
    #
    def consistency(self, mode=None):
        """

        Perform a number of data consistency checks, and return a set of UIDs
        for entities which have been found to be inconsistent.
        The method accepts a single parameter `mode` which can be a list of
        strings defining what consistency checks are to be performed.  Valid
        strings are:

            'state_model' : check if all entity states are in adherence to the
                            respective entity state model
            'event_model' : check if all entity events are in adherence to the
                            respective entity event model
            'timestamps'  : check if events and states are recorded with correct
                            ordering in time.

        If not specified, the method will execute all three checks.

        After this method has been run, each checked entity will have more
        detailed consistency information available via:

            entity.consistency['state_model'] (bool)
            entity.consistency['event_model'] (bool)
            entity.consistency['timestamps' ] (bool)
            entity.consistency['log' ]        (list of strings)

        The boolean values each indicate consistency of the respective test, the
        `log` will contain human readable information about specific consistency
        violations.
        """

        # FIXME: we could move the method to the entity, so that we can check
        #        consistency for each entity individually.


        self._rep.header('running consistency checks')

        ret   = list()
        MODES = ['state_model', 'event_model', 'timestamps']

        if not mode:
            mode = MODES

        if not isinstance(mode, list):
            mode = [mode]

        for m in mode:
            if m not in MODES:
                raise ValueError('unknown consistency mode %s' % m)

        if 'state_model' in mode:
            ret.extend(self._consistency_state_model())

        return list(set(ret))  # make list unique


    # --------------------------------------------------------------------------
    #
    def _consistency_state_model(self):

        ret = list()  # list of inconsistent entity IDs

        for et in self.list('etype'):

            self._rep.info('%s state model\n' % et)
            sm = self.describe('state_model', etype=et)
            sv = self.describe('state_values', etype=et)[et]['state_values']

          # print
          # print et
          # print sv
          # print

            for e in self.get(etype=et):

                es = e.states

                if not sv:
                    if es:
                        self._rep.warn('  %-30s : %s' % (et, es.keys()))
                        e._consistency['state_model'] = None
                    continue

                self._rep.info('  %-30s :' % e.uid)

                missing = False   # did we miss any state so far?
                final_v = sorted(sv.keys())[-1]
                final_s = sv[final_v]

                if not isinstance(final_s, list):
                    final_s = [final_s]

                sm_ok    = True
                sm_log   = list()
                miss_log = list()
                for v,s in sv.iteritems():

                    if not s:
                        continue

                    if not isinstance(s, list):
                        s = [s]

                    # check if we have that state
                    found = None
                    for _s in s:
                        if _s in es:
                            found = _s
                            break

                    if found:

                        if missing:

                            if found not in final_s:
                                # found a state after a previous one was missing,
                                # but we are not final.  Oops
                                self._rep.warn('+')
                                sm_log.extend(miss_log)
                                miss_log = list()
                                sm_ok = False
                                continue

                    else:
                        if s == final_s:
                            # no final state?  Oops
                            self._rep.error('no final state! ')
                            sm_ok = False
                            sm_log.append('missing final state')
                            continue

                        else:
                            # Hmm, might be ok.  Lets see...
                            missing = True
                            self._rep.warn('*')
                            miss_log.append('missing state(s) %s' % s)
                            continue

                    self._rep.ok('+')

                e._consistency['state_model'] = sm_ok
                e._consistency['log'].extend(sm_log)

                if not sm_ok:
                    ret.append(e.uid)

                self._rep.plain('\n')

        return ret


# ------------------------------------------------------------------------------

