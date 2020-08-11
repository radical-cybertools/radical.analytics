# pylint: disable=W0102,W0212

import os
import sys
import copy
import tarfile

import pickle as pickle

import more_itertools as mit
import radical.utils  as ru

from .entity import Entity


# ------------------------------------------------------------------------------
#
class Session(object):

    # --------------------------------------------------------------------------
    #
    def __init__(self, src, stype, sid=None, _entities=None, _init=True):
        '''
        Create a radical.analytics session for analysis.

        The session is created from a set of traces, which usually have been
        produced by a Session object in the RCT stack, such as radical.pilot or
        radical.entk. Profiles are accepted in two forms: in a directory, or in
        a tarball (of such a directory).  In the latter case, the tarball are
        extracted into `$TMP`, and then handled just as the directory case.

        If no `sid` (session ID) is specified, that ID is derived from the
        directory name.

        '''

        if _init:
            # if no sid is given, derive it from the src path
            sid, src, tgt, ext = self._get_sid(sid, src)
        else:
            assert sid
            assert src
            tgt = None

        if tgt and not os.path.exists(tgt):

            # need to extract
            print(('extract tarball to %s' % tgt))
            try:
                if ext in ['tbz', 'tar.bz', 'tbz2', 'tar.bz2']:
                    tf = tarfile.open(name=src, mode='r:bz2')
                    tf.extractall(path=os.path.dirname(tgt))
                elif ext in ['tgz, tar.gz']:
                    tf = tarfile.open(name=src, mode='r:gz')
                    tf.extractall(path=os.path.dirname(tgt))
                else:
                    raise ValueError('cannot handle extension %s' % ext)

            except Exception as e:
                raise RuntimeError('Cannot extract tarball: %s' % repr(e))

        self._sid   = sid
        self._src   = src
        self._stype = stype

      # print 'sid: %s [%s]' % (sid, stype)
      # print 'src: %s'      % src

        if stype == 'radical':

            # src is expected to point either to a single profile, or to
            # a directory tree containing profiles
            if not src:
                raise ValueError('RA session types need `src` specified')

            profiles = list()
            if os.path.isfile(src):
                profiles.append(src)
            else:
                def _walkdir(path, profiles=[]):
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            if f.endswith('.prof'):
                                profiles.append('%s/%s' % (root, f))
                        for d in dirs:
                            _walkdir('%s/%s' % (path, d), profiles)
                        return profiles
                profiles = _walkdir(src)

            profiles                = ru.read_profiles(profiles, sid=sid)
            self._profile, accuracy = ru.combine_profiles(profiles)
            self._description       = {'tree'     : dict(),
                                       'entities' : list(),
                                       'hostmap'  : dict(),
                                       'accuracy' : 0.0}

        elif stype == 'radical.pilot':

            try:
                import radical.pilot.utils as rpu
            except:
                raise RuntimeError('radical.analytics requires the '
                                   'radical.pilot module to analyze this '
                                   'session - please install it.')

            self._profile, accuracy, hostmap \
                              = rpu.get_session_profile    (sid=sid, src=self._src)
            self._description = rpu.get_session_description(sid=sid, src=self._src)

            self._description['accuracy'] = accuracy
            self._description['hostmap']  = hostmap


        elif stype == 'radical.entk':

            try:
                import radical.entk.utils as reu
            except:
                raise RuntimeError('radical.analytics requires the '
                                   'radical.entk module to analyze this '
                                   'session - please install it.')

            self._profile, accuracy, hostmap \
                              = reu.get_session_profile    (sid=sid, src=self._src)
            self._description = reu.get_session_description(sid=sid, src=self._src)

            self._description['accuracy'] = accuracy
            self._description['hostmap']  = hostmap


        else:
            raise ValueError('unsupported session type [%s]' % stype)


        self._t_start = None
        self._t_stop  = None
        self._ttc     = None
        self._log     = ru.Logger('radical.analytics')
        self._rep     = ru.Reporter('radical.analytics')


        # user defined time offset
        self._tzero   = 0.0

        # internal state is represented by a dict of entities:
        # dict keys are entity uids (which are assumed to be unique per
        # session), dict values are ra.Entity instances.
        self._entities = dict()
        if _init:
            self._initialize_entities(self._profile)

        # we do some bookkeeping in self._properties where we keep a list of
        # property values around which we encountered in self._entities.
        self._properties = dict()
        if _init:
            self._initialize_properties()

      # print('session loaded')

        # FIXME: we should do a sanity check that all encountered states and
        #        events are part of the respective state and event models
      # self.consistency()


    # --------------------------------------------------------------------------
    #
    @staticmethod
    def _get_sid(sid, src):

        tgt = None
        ext = None

        if not os.path.exists(src):
            raise ValueError('src [%s] does not exist' % src)

        if os.path.isdir(src):
            pass

        elif os.path.isfile(src):

            # src is afile - we assume its a tarball and extract it
            if  src.endswith('.prof'):
                # use as is
                tgt = src

            elif src.endswith('.tgz') or \
                 src.endswith('.tbz')    :
                tgt = src[:-4]
                ext = src[-3:]

            elif src.endswith('.tbz2'):
                tgt = src[:-5]
                ext = src[-4:]

            elif src.endswith('.tar.gz') or \
                 src.endswith('.tar.bz')    :
                tgt = src[:-7]
                ext = src[-6:]

            elif src.endswith('.tar.bz2'):
                tgt = src[:-8]
                ext = src[-7:]

            elif src.endswith('.prof'):
                tgt = None
                ext = None

            else:
                raise ValueError('src does not look like a tarball or profile')

        if not sid:

            if tgt: to_check = tgt
            else  : to_check = src

            if to_check.endswith('/'):
                to_check = src[:-1]
            sid = os.path.basename(to_check)

        return sid, src, tgt, ext


    # --------------------------------------------------------------------------
    #
    def __getstate__(self):

        state = {
                 'sid'         : self._sid,
                 'src'         : self._src,
                 'stype'       : self._stype,
                 'profile'     : self._profile,
                 'description' : self._description,

                 't_start'     : self._t_start,
                 't_stop'      : self._t_stop,
                 'ttc'         : self._ttc,

                 'entities'    : self._entities,
                 'properties'  : self._properties,
                }

        return state


    # --------------------------------------------------------------------------
    #
    def __setstate__(self, state):

        self._sid         = state['sid']
        self._src         = state['src']
        self._stype       = state['stype']
        self._profile     = state['profile']
        self._description = state['description']

        self._t_start     = state['t_start']
        self._t_stop      = state['t_stop']
        self._ttc         = state['ttc']

        self._entities    = state['entities']
        self._properties  = state['properties']

        self._log         = ru.Logger('radical.analytics')
        self._rep         = ru.Reporter('radical.analytics')


    # --------------------------------------------------------------------------
    #
    @staticmethod
    def create(src, stype, sid=None, _entities=None, _init=True, cache=True):

        sid, src, _, _ = Session._get_sid(sid, src)
        base  = ru.get_radical_base('radical.analytics.cache')
        cache = '%s/%s.pickle' % (base, sid)

        if _entities or not cache:
            # no caching
            session = Session(src, stype, sid, _entities, _init)

        try:
            with open(cache, 'rb') as fin:
                data = fin.read()
                session = pickle.loads(data)
         #      import pprint
         #      j = ru.read_json("%s/%s.json" % (src, sid))
         #      rd = j['pilot'][0]['resource_details']
         #      session.get(etype='pilot')[0].cfg['resource_details'] = rd
         #      pprint.pprint(session.get(etype='pilot')[0].cfg)
         #  with open(cache, 'wb') as fout:
         #    # session = Session(src, stype, sid, _entities, _init)
         #      fout.write(pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL))

        except Exception as e:
            print(('cache read failed: %s' % e))
            with open(cache, 'wb') as fout:
                session = Session(src, stype, sid, _entities, _init)
                fout.write(pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL))

        return session


    # --------------------------------------------------------------------------
    #
    def __deepcopy___(self, memo):

        cls = self.__class__
        ret = cls(sid=self._sid, src=None, stype=self._stype, _init=False)

        memo[id(self)] = ret

        for k, v in list(self.__dict__.items()):
            setattr(ret, k, copy.deepcopy(v, memo))

        return ret


    # --------------------------------------------------------------------------
    #
    def _reinit(self, entities):
        '''
        After creating a session clone, we have identical sets of descriptions,
        profiles, and entities.  However, if we apply a filter during the clone
        creation, we end up with a deep copy which should have a **different**
        set of entities.  This method applies that new entity set to such a
        cloned session.
        '''

        self._entities = entities

        # FIXME: we may want to filter the session description etc. wrt. to the
        #        entity types remaining after a filter.


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
        return self._sid

    @property
    def stype(self):
        return self._stype


    # --------------------------------------------------------------------------
    #
    def _initialize_entities(self, profile):
        '''
        Populates self._entities from profile and self._description.

        NOTE: We derive entity types via some heuristics for now: we assume the
        first part of any dot-separated uid to signify an entity type.
        '''

        # create entities from the profile events:
        entity_events = dict()

        for event in profile:
            uid = event[ru.UID]

            if uid not in entity_events:
                entity_events[uid] = list()
            entity_events[uid].append(event)

        # for all uids found,  create and store an entity.  We look up the
        # entity type in one of the events (and assume it is consistent over
        # all events for that uid)
        for uid,events in list(entity_events.items()):
            etype   = events[0][ru.ENTITY]
            details = self._description.get('tree', dict()).get(uid, dict())
            details['hostid'] = self._description.get('hostmap', dict()).get(uid)
            self._entities[uid] = Entity(_uid=uid,
                                         _etype=etype,
                                         _profile=events,
                                         _details=details)


    # --------------------------------------------------------------------------
    #
    def _initialize_properties(self):
        '''
        populate `self._properties` from `self._entities`.  `self._properties`∫
        has the following format::

            {
              'state' : {
                'NEW'      : 10,
                'RUNNING'  :  8,
                'DONE      :  7,
                'FAILED'   :  1,
                'CANCELED' :  2
              }
            }

        We count how often any property value appears in the current set of
        entities.

        RA knows exactly 4 properties:
          - uid   (entity idetifiers)
          - etype (type of entities)
          - event (names of events)
          - state (state identifiers)
        '''

        # FIXME: initializing properties can be expensive, and we might not
        #        always need them anyway.  So we can lazily defer this
        #        initialization stop until the first query which requires them.

        # we do *not* look at profile and descriptions anymore, those are only
        # evaluated once on construction, in `_initialize_entities()`.  Now we
        # don't parse all that stuff again, but only re-initialize after
        # in-place filtering etc.
        self._properties = {'uid'   : dict(),
                            'etype' : dict(),
                            'event' : dict(),
                            'state' : dict()}

        if self._entities:
            self._t_start = sys.float_info.max
            self._t_stop  = sys.float_info.min

        for euid,e in list(self._entities.items()):

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
                name = event[ru.EVENT]
                if name not in self._properties['event']:
                    self._properties['event'][name] = 0
                self._properties['event'][name] += 1

        if self._entities:
            self._ttc = self._t_stop - self._t_start


    # --------------------------------------------------------------------------
    #
    def _apply_filter(self, etype=None, uid=None, state=None,
                            event=None, time=None):

        # iterate through all self._entities and collect UIDs of all entities
        # which match the given set of filters (after removing all events which
        # are not in the given time ranges)
        if not etype: etype = list()
        if not uid  : uid   = list()
        if not state: state = list()
        if not event: event = list()
        if not time : time  = list()

        if etype and not isinstance(etype, list): etype = [etype]
        if uid   and not isinstance(uid  , list): uid   = [uid  ]
        if state and not isinstance(state, list): state = [state]
        if event and not isinstance(event, list): event = [event]

        if time and len(time) and not isinstance(time[0], list): time = [time]

        ret = list()
        for eid,entity in list(self._entities.items()):

            if etype and entity.etype not in etype: continue
            if uid   and entity.uid   not in uid  : continue

            if state:
                match = False
                for s,stuple in list(entity.states.items()):
                    if time and not ru.in_range(stuple[ru.TIME], time):
                        continue
                    if s in state:
                        match = True
                        break
                if not match:
                    continue

            if event:
                match = False
                for etuple in entity.events:
                    if time and not ru.in_range(etuple[ru.TIME], time):
                        continue
                    if etuple[ru.EVENT] in event:
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

        for uid,entity in list(self._entities.items()):
            print(('\n\n === %s' % uid))
            entity.dump()
            for event in entity.events:
                print(('  = %s' % event))
                for e in entity.events[event]:
                    print(('    %s' % e))


    # --------------------------------------------------------------------------
    #
    def list(self, pname=None):

        if not pname:
            # return the name of all known properties
            return list(self._properties.keys())

        if isinstance(pname, list):
            return_list = True
            pnames = pname
        else:
            return_list = False
            pnames = [pname]

        ret = list()
        for _pname in pnames:
            if _pname not in self._properties:
                raise KeyError('no such property known (%s) / %s'
                        % (_pname, list(self._properties.keys())))
            ret.append(list(self._properties[_pname].keys()))

        if return_list: return ret
        else          : return ret[0]


    # --------------------------------------------------------------------------
    #
    def get(self, etype=None, uid=None, state=None, event=None, time=None):

        uids = self._apply_filter(etype=etype, uid=uid, state=state,
                                  event=event, time=time)
        return [self._entities[_uid] for _uid in uids]


    # --------------------------------------------------------------------------
    #
    def filter(self, etype=None, uid=None, state=None, event=None, time=None,
               inplace=True):

        uids = self._apply_filter(etype=etype, uid=uid, state=state,
                                  event=event, time=time)

        if inplace:
            # filter our own entity list, and refresh the entity based on
            # the new list
            if uids != list(self._entities.keys()):
                self._entities = {uid:self._entities[uid] for uid in uids}
                self._initialize_properties()
            return self

        else:
            # create a new session with the resulting entity list
            ret = Session(sid=self._sid, stype=self._stype, src=self._src,
                          _init=False)
            ret._reinit(entities={uid:self._entities[uid] for uid in uids})
            ret._initialize_properties()
            return ret


    # --------------------------------------------------------------------------
    #
    def describe(self, mode=None, etype=None):

        if mode not in [None, 'state_model', 'state_values',
                              'event_model', 'relations',
                              'statistics']:
            raise ValueError('describe parameter "mode" invalid')

        if not etype and not mode:
            # no entity filter applied: return the full description
            return self._description

        if mode == 'statistics':
            return self._properties

        if not etype:
            etype = self.list('etype')

        if not isinstance(etype,list):
            etype = [etype]

        ret = dict()
        for et in etype:

            state_model  = None
            state_values = None
            event_model  = None

            if et in self._description.get('entities', dict()):
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

            rel = self._description.get('tree', dict())
            for p in parent_uids:

                ret[p] = list()
                if p not in rel:
                    print(('inconsistent : no relations for %s' % p))
                    continue

                for c in rel[p]['children']:
                    if c in child_uids:
                        ret[p].append(c)

        return ret


    # --------------------------------------------------------------------------
    #
    def ranges(self, state=None, event=None, time=None, collapse=True):
        '''
        Gets a set of initial and final conditions, and computes time ranges in
        accordance to those conditions from all session entities. The resulting
        set of ranges is then collapsed to the minimal equivalent set of ranges
        covering the same set of times.

        Please refer to the :class:`Entity.ranges` documentation on detail on
        the constrain parameters.

        Setting 'collapse' to 'True' (default) will prompt the method to
        collapse the resulting set of ranges.
        '''

        ranges = list()
        for uid,entity in list(self._entities.items()):
            try:
                ranges += entity.ranges(state, event, time, collapse=False)
            except ValueError:
                print(('no ranges for %s' % uid))
                # ignore entities for which the conditions did not apply
                # pass

        if not ranges:
            return []

        if collapse:
            ret = ru.collapse_ranges(ranges)
        else:
            ret = ranges

        # sort ranges by start time and return
        return sorted(ret, key=lambda r: r[1])


    # --------------------------------------------------------------------------
    #
    def timestamps(self, state=None, event=None, time=None, first=False):
        '''
        This method accepts a set of conditions, and returns the list of
        timestamps for which those conditions applied, i.e., for which state
        transitions or events are known which match the given 'state' or 'event'
        parameter.  If no match is found, an empty list is returned.

        Both `state` and `event` can be lists, in which case the union of all
        timestamps are returned.

        The `time` parameter is expected to be a single tuple, or a list of
        tuples, each defining a pair of start and end time which are used to
        constrain the matching timestamps.

        If `first` is set to `True`, only the timestamps for the first matching
        events (per entity) are returned.

        The returned list will be sorted.
        '''

        ret = list()
        for _,entity in list(self._entities.items()):
            tmp = entity.timestamps(state=state, event=event, time=time)
            if tmp and first:
                ret.append(tmp[0])
            else:
                ret += tmp

        return sorted(ret)


    # --------------------------------------------------------------------------
    #
    def duration(self, state=None, event=None, time=None, ranges=None):
        '''
        This method accepts the same set of parameters as the `ranges()` method,
        and will use the `ranges()` method to obtain a set of ranges.  It will
        return the sum of the durations for all resulting & collapsed ranges.

        Example::

           session.duration(state=[rp.NEW, rp.FINAL]))

        where `rp.FINAL` is a list of final unit states.
        '''

        if not ranges:
            ranges = self.ranges(state, event, time)

        else:
            assert(not state)
            assert(not event)
            assert(not time)

            # make sure the ranges are collapsed (although they likely are
            # already...)
            ranges = ru.collapse_ranges(ranges)

        return sum(r[1] - r[0] for r in ranges)


    # --------------------------------------------------------------------------
    #
    def concurrency(self, state=None, event=None, time=None, sampling=None):
        '''
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

        Returned is an ordered list of tuples::

            [ [time_0, concurrency_0],
              [time_1, concurrency_1],
              ...
              [time_n, concurrency_n] ]

        where `time_n` is represented as `float`, and `concurrency_n` as `int`.

        Example::

            session.filter(etype='unit').concurrency(state=[rp.AGENT_EXECUTING,
                rp.AGENT_STAGING_OUTPUT_PENDING])

        '''

        INC =  1  # increase concurrency
        DEC = -1  # decrease concurrency

        ranges = list()
        for _,e in list(self._entities.items()):
            ranges += e.ranges(state, event, time)

        if not ranges:
            return []

        times = list()
        # get all start and end times for all ranges.  The start of a range will
        # increase concurrency by one at that time stamp, and the end will
        # decrease it by one again.
        for r in ranges:
            times.append([r[0], INC])
            times.append([r[1], DEC])

        # sort those times
        times.sort()

        # get the overall concurrency data
        conc = 0
        data = list()  # [[time, concurrency], ...]
        for time, val in times:
            conc += val
            data.append([time, conc])

        # collapse time stamps (use last value on same time stamps)
        collapsed = list()
        last      = data[0]
        for time, val in data[1:]:
            if time != last[0]:
                collapsed.append(last)
            last = [time, val]

        # append last time
        collapsed.append(last)

        # make sure we start at zero (at time of first event)
        collapsed.insert(0, [collapsed[0][0], 0])

        if not sampling:
            # return as is
            ret = collapsed

        else:
            # select data points according to sampling
            # get min time, and create timestamps at regular intervals
            t     = times[0][0]
            ret   = list()
            for time, val in collapsed:
                while time >= t:
                    ret.append(t, val)
                    t += sampling

            # append last time stamp if it is not appended, yet
            if ret[-1] != [t, val]:
                ret.append([t, val])

        return ret


    # --------------------------------------------------------------------------
    #
    def rate(self, state=None, event=None, time=None, sampling=None,
            first=False):
        '''
        This method accepts the same parameters as the `timestamps()` method: it
        will count all matching events and state transitions as given, and will
        return a time series of the rate of how many of those events and/or
        transitions occured per second.

        The additional parameter `sampling` determines the exact points in time
        for which the rate is computed, and thus determines the sampling rate
        for the returned time series.  If not specified, the time series will
        contain all points at which and event occured, and the rate value will
        only be determined by the time passed between two consequtuve events.
        If specified, it is interpreted as second (float) interval at which,
        after the starting point (begin of first event matching the filters) the
        rate is computed.

        Returned is an ordered list of tuples::

          [ [time_0, rate_0] ,
            [time_1, rate_1] ,
            ...
            [time_n, rate_n] ]

        where `time_n` is represented as `float`, and `rate_n` as `int`.

        The `time` parameter is expected to be a single tuple, or a list of
        tuples, each defining a pair of start and end time which are used to
        constrain the resulting time series.

        The 'first' is defined, only the first matching event fir the selected
        entities is considered viable.

        Example::

           session.filter(etype='unit').rate(state=[rp.AGENT_EXECUTING])
        '''

        timestamps = self.timestamps(event=event, state=state, time=time,
                                     first=first)

        if not timestamps:
            # nothing to do
            return []


        times = list()
        if sampling:
            # get min and max timestamp, and create sampling points at
            # regular intervals
            r_min = timestamps[0]
            r_max = timestamps[-1]

            t = r_min
            while t < r_max:
                times.append(t)
                t += sampling
            times.append(r_max)

        else:
            # we create an entry at all timestamps
            times = timestamps[:]

        if not times:
            # nothing to do
            return []

        # we need to make sure that no two consecutive timestamps are the same,
        # as that would lead to a division by zero later on
        times = sorted(set(times))

      # import pprint
      # pprint.pprint(times)

        # make sure we start in correct state, and first data point does not
        # occur before sampling starts
        assert timestamps[0] >= times[0]

        # we have the time sequence, now compute event rate at those points
        ts_idx  = 0                # index into the list of timestamps
        ts_len  = len(timestamps)  # number of timestamps
        ret     = list()           # our rate time series
        t_start = times[0]         # current samplint window
        t_stop  = times[0]

        for t in times[1:]:
            t_start = t_stop       # slide sampling window to next sample time
            t_stop  = t
            cnt     = 0            # reset event counter


            while ts_idx < ts_len:
                if timestamps[ts_idx] <= t_stop:
                    # timestamp is in range, count event
                    cnt += 1
                else:
                    # we need to slide the sampling window
                    break
                # go to next timestamp
                ts_idx += 1

          # print 'window: %f - %f (%f) : %5d' % \
          #         (t_start, t_stop, t_stop - t_start, cnt)

            # sampling window completed - store rate of events in sample
            ret.append([t_stop, cnt / (t_stop - t_start)])

        return ret


    # --------------------------------------------------------------------------
    #
    def utilization(self, metrics):

        if self._stype != 'radical.pilot':
            raise ValueError('session utilization is only available on '
                             'radical.pilot sessions')

        import radical.pilot as rp

        provided  = rp.utils.get_provided_resources(self)
        consumed  = rp.utils.get_consumed_resources(self)
        stats_abs = {'total':   0.0}
        stats_rel = {'total': 100.0}
        total     = 0.0

        for pid in provided['total']:
            for box in provided['total'][pid]:
                stats_abs['total'] += (box[1] - box[0]) * \
                                      (box[3] - box[2]  + 1)
        total = stats_abs['total']

        for metric in metrics:
            if isinstance(metric, list):
                name  = metric[0]
                parts = metric[1]
            else:
                name  = metric
                parts = [metric]

            if name not in stats_abs:
                stats_abs[name] = 0.0

            for part in parts:
                for uid in consumed[part]:
                    for box in consumed[part][uid]:
                        stats_abs[name] += (box[1] - box[0]) * \
                                           (box[3] - box[2]  + 1)

        info  = ''
        info += '%s [%d]\n' % (self.uid, len(self.get(etype='unit')))

        for metric in metrics + ['total']:
            if isinstance(metric, list):
                name  = metric[0]
                parts = metric[1]
            else:
                name  = metric
                parts = ''

            val = stats_abs[name]
            if val == 0.0: glyph = '!'
            else         : glyph = ''
            rel = 100.0 * val / total
            stats_rel[name] = rel
            info += '    %-20s: %14.3f  %8.3f%%  %2s  %s\n' \
                  % (name, val, rel, glyph, parts)

        have = 0.0
        over = 0.0
        work = 0.0
        for metric in sorted(stats_abs.keys()):
            if metric == 'total':
                have  += stats_abs[metric]
            else:
                if metric == 'Execution Cmd':
                    work  += stats_abs[metric]
                else:
                    over  += stats_abs[metric]

        miss = have - over - work

        rel_over = 100.0 * over / total
        rel_work = 100.0 * work / total
        rel_miss = 100.0 * miss / total

        stats_abs['Other'] = miss
        stats_rel['Other'] = rel_miss

        info += '\n'
        info += '    %-20s: %14.3f  %8.3f%%\n' % ('total', have, 100.0)
        info += '    %-20s: %14.3f  %8.3f%%\n' % ('over',  over, rel_over)
        info += '    %-20s: %14.3f  %8.3f%%\n' % ('work',  work, rel_work)
        info += '    %-20s: %14.3f  %8.3f%%\n' % ('miss',  miss, rel_miss)

        return provided, consumed, stats_abs, stats_rel, info


    # --------------------------------------------------------------------------
    #
    # def utilization_bak(self, owner, consumer, resource, owner_events=None,
    #                                                   consumer_events=None):
    #     '''
    #     Parms:
    #         owner          : The entity name of the owner of the resources
    #         consumer       : The ename of the entity that consumes the resources
    #                         owned by owner
    #         resource       : The type of resources whose utilization is requested,
    #                         eg. Cores, Memory, GPUS etc.
    #         owner_events   : A list of owner's/owners' events that will be used as
    #                         starting and ending points for the resource ownership.
    #         consumer_events: A list of owner's/owners' events that will be used as
    #                         starting and ending points for resource consumption.

    #     Based on these parameters the resources of the owners are collected, as
    #     well as, the times when the consumer(s) used those resources.

    #     Returned is a dictionary of the form::

    #         { 'owner_0': {'range'      : owner_range,
    #                       'resources'  : resource_size,
    #                       'utilization': [[time_0, resource_utilization_0],
    #                                       [time_1, resource_utilization_1],
    #                                       ...
    #                                       [time_n, resource_utilization_n]]},
    #           'owner_1': {'range'      : owner_range,
    #                       'resources'  : resource_size,
    #                       'utilization': [[time_0, resource_utilization_0],
    #                                       [time_1, resource_utilization_1],
    #                                       ...
    #                                       [time_n, resource_utilization_n]]},
    #           ...
    #           'owner_n': {'range'      : owner_range,
    #                       'resources'  : resource_size,
    #                       'utilization': [[time_0, resource_utilization_0],
    #                                       [time_1, resource_utilization_1],
    #                                       ...
    #                                       [time_n, resource_utilization_n]]}

    #     where `time_n` is represented as `float`, `resource_utilization_n` as
    #     `int`, and resource_size is the total resources the owner has.


    #     Example::

    #         s.utilization(owner          = 'pilot',
    #                       consumer       = 'unit',
    #                       resource       = 'cores',
    #                       owner_events   = [{ru.EVENT: 'bootstrap_0_start'},
    #                                         {ru.EVENT: 'bootstrap_0_stop' }])
    #                       consumer_events= [{ru.EVENT: 'exec_start'},
    #                                         {ru.EVENT: 'exec_stop' }])
    #     '''
    #     ret = dict()

    #     # Filter the session to get a session of the owners. If that is empty
    #     # return an empty dict

    #     relations = self .describe('relations', [owner, consumer])
    #     if not relations:
    #         return dict()

    #     owners = self.filter(etype=owner, inplace=False)
    #     if not owners:
    #         return dict()

    #     # Filter the self to get the consumers. If none are found, return an
    #     # empty dict.
    #     #
    #     # FIXME: this should return an dict with zero utilization over the full
    #     #        time range the resource exist.
    #     #
    #     for o in owners.get():
    #         owner_id        = o.uid
    #         owner_resources = o.description.get(resource)
    #         owner_range     = o.ranges(event=owner_events)

    #         consumers = self.filter(etype=consumer, uid=relations[owner_id],
    #                                 inplace=False)
    #         if not consumers:
    #             util = [0]

    #         else:
    #             # Go through the consumer entities and create two dictionaries.
    #             # The first keeps track of how many resources each consumer
    #             # consumes, and the second has the ranges based on the events.
    #             consumer_resources = dict()
    #             consumer_ranges    = dict()

    #             for c in consumers.get():

    #                 ranges  = c.ranges(event=consumer_events)
    #                 cons_id = c.uid

    #                 resources_acquired = 0
    #                 if resource == 'cores':
    #                     cores   = c.description['cpu_processes'] * \
    #                               c.description['cpu_threads']
    #                     resources_acquired += cores
    #                 elif resource == 'gpus':
    #                     gpus    = c.description['gpu_processes']
    #                     resources_acquired += len(gpus)
    #                 else:
    #                     raise ValueError('unsupported utilization resource')

    #                 consumer_resources[cons_id] = resources_acquired

    #                 # Update consumer_ranges if there is at least one range
    #                 if ranges:
    #                     consumer_ranges.update({cons_id: ranges})


    #             # Sort consumer_ranges based on their values. This command
    #             # returns a dictionary, which is sorted based on the first value
    #             # of each entry. In the end the key, are out of order but the
    #             # values are.
    #             consumer_ranges = sorted(iter(list(consumer_ranges.items())),
    #                                      key=lambda k_v: (k_v[1][0],k_v[0]))

    #             # Create a timeseries that contains all moments in consumer
    #             # ranges and sort. This way we have a list that has time any
    #             # change has happened.
    #             times = list()
    #             for cons_id,ranges in consumer_ranges:
    #                 for r in ranges:
    #                     times.append(r[0])
    #                     times.append(r[1])
    #             times.sort()

    #             # we have the time sequence, now compute utilization
    #             # at those points
    #             util = list()
    #             for t in times:
    #                 cnt = 0
    #                 for cons_id,ranges in consumer_ranges:
    #                     for r in ranges:
    #                         if t >= r[0] and t <= r[1]:
    #                             cnt += consumer_resources[cons_id]

    #                 util.append([t, cnt])

    #         ret[owner_id] = {'range'      : owner_range,
    #                          'resources'  : owner_resources,
    #                          'utilization': util}
    #     return ret


    # --------------------------------------------------------------------------
    #
    def consistency(self, mode=None):
        '''
        Performs a number of data consistency checks, and returns a set of UIDs
        for entities which have been found to be inconsistent. The method
        accepts a single parameter `mode` which can be a list of strings
        defining what consistency checks are to be performed. Valid strings are:

        - state_model: check if all entity states are in adherence to the
          respective entity state model
        - event_model: check if all entity events are in adherence to the
          respective entity event model
        - timestamps: check if events and states are recorded with correct
          ordering in time.

        If not specified, the method will execute all three checks.

        After this method has been run, each checked entity will have more
        detailed consistency information available via::

            entity.consistency['state_model'] (bool)
            entity.consistency['event_model'] (bool)
            entity.consistency['timestamps' ] (bool)
            entity.consistency['log' ]        (list of strings)

        The boolean values each indicate consistency of the respective test, the
        `log` will contain human readable information about specific consistency
        violations.
        '''

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
    def usage(self, alloc_entity, alloc_events,
                    block_entity, block_events,
                    use_entity,   use_events):
        '''
        This method creates a dict with three entries: `alloc`, `block`, `use`.
        Those three dict entries in turn have a a dict of entity IDs for all
        entities which have blocks in the respective category, and foreach of
        those entity IDs the dict values will be a list of rectangles.

        A resource is considered:

        - `alloc` (allocated) when it is owned by the RCT application;
        - `block` (blocked) when it is reserveed for a specific task;
        - `use` (used) when it is utilized by that task.

        Each of the rectangles represents a continuous block of resources which
        is alloced/blocked/used:

        - x_0 time when `alloc/block/usage` begins;
        - x_1 time when `alloc/block/usage` ends;
        - y_0 lowest index of a continuous block of resource IDs;
        - y_1 highest index of a continuous block of resource IDs.

        Any specific entity (pilot, task) can have a **set** of such resource
        blocks, for example, a task might be placed over multiple,
        non-consecutive nodes:

        - gpu and cpu resources are rendered as separate blocks (rectangles).

        Args:
            alloc_entity (Entity): :class:`Entity` instance which allocates
                resources
            alloc_events (list): event tuples which specify allocation time
            block_entity (Entity): :class:`Entity` instance which blocks
                resources
            block_events (list): event tuples which specify blocking time
            use_entity (Entity): :class:`Entity` instance which uses resources
            use_events (list): event tuples which specify usage time

        Example::

            usage('pilot', [{ru.STATE: None, ru.EVENT: 'bootstrap_0_start'},
                            {ru.STATE: None, ru.EVENT: 'bootstrap_0_stop' }],
                  'unit' , [{ru.STATE: None, ru.EVENT: 'schedule_ok'      },
                            {ru.STATE: None, ru.EVENT: 'unschedule_stop'  }],
                  'unit' , [{ru.STATE: None, ru.EVENT: 'exec_start'       },
                            {ru.STATE: None, ru.EVENT: 'exec_stop'        }])
        '''

        # this is currently only supported for RP sessions, as we only know for
        # pilots and units how to dig resource information out of session and
        # entity metadata.
        assert(self.stype == 'radical.pilot'), \
               'stype %s unsupported' % self._stype

        # for RP sessions, create resource indices which can be used to
        # determine the y-axis values for the rectangles.  This is basically
        # a dict of node_names for each alloc_entity which points to two indexes
        # for each node: one starting index for GPUs, and one for CPU cores
        res_idx = dict()

        idx = 0
        for ae in self.get(etype=alloc_entity):
            uid   = ae.uid
            nodes = ae.cfg['resource_details']['rm_info']['node_list']
            cpn   = ae.cfg['resource_details']['rm_info']['cores_per_node']
            gpn   = ae.cfg['resource_details']['rm_info']['gpus_per_node']

            if ae.uid not in res_idx:
                res_idx[ae.uid] = dict()

            res_idx[ae.uid]['_min'] = idx

            for n in nodes:
                res_idx[ae.uid][n[1]] = [[idx      , idx + cpn       - 1],
                                         [idx + cpn, idx + cpn + gpn - 1]]
                idx += cpn
                idx += gpn

            res_idx[ae.uid]['_max'] = idx - 1

        # ----------------------------------------------------------------------
        # RP specific helper method to convert given entity information into
        # a set of y-value ranges.  This returns a tuple of lists where each
        # list contains tuples of resource indexes (y-values)
        def get_res_idx(entity):

            if entity.etype == 'pilot':

              # print '----'
              # print entity.uid
              # import pprint
              # pprint.pprint(res_idx[entity.uid])

                # we assume min/max to cover CPU and GPU
                return [[[res_idx[entity.uid]['_min'],
                          res_idx[entity.uid]['_max']]], []]

            elif entity.etype == 'unit':

                # find owning pilot
                pid = entity.cfg.get('pilot')
                if not pid:
                    # no resources used
                    return [[],[]]

                cpu_idx = list()
                gpu_idx = list()
                for slot in entity.cfg['slots']['nodes']:
                    node_id = slot['uid']
                    for cslot in slot['core_map']:
                        for c in cslot:
                            cpu_idx.append(res_idx[pid][node_id][0][0] + c)
                    for gslot in slot['gpu_map']:
                        for g in gslot:
                            gpu_idx.append(res_idx[pid][node_id][1][0] + g)

                # identify continuous groups of y-values and return
                return [
                        [list(g) for g in mit.consecutive_groups(cpu_idx)],
                        [list(g) for g in mit.consecutive_groups(gpu_idx)]
                       ]
        # ----------------------------------------------------------------------

        ret = {'alloc': dict(),
               'block': dict(),
               'use'  : dict()}

        etypes = {'alloc': {'etype' : alloc_entity,
                            'events': alloc_events},
                  'block': {'etype' : block_entity,
                            'events': block_events},
                  'use'  : {'etype' : use_entity,
                            'events': use_events}}

        for entity in self.get():

            for mode in ['alloc', 'block', 'use']:

                if etypes[mode]['etype'] == entity.etype:

                    event_list = etypes[mode]['events']
                    if not event_list:
                        continue

                    if not isinstance(event_list[0], list):
                        event_list = [event_list]

                    uid = entity.uid
                    if uid not in ret[mode]:
                        ret[mode][uid] = list()

                    for events in event_list:
                        assert len(events) == 2

                        y_values = get_res_idx(entity)
                        t_values = entity.ranges(event=events)

                      # print
                      # print uid
                      # print events
                      #
                      # import pprint
                      # pprint.pprint(t_values)
                      # pprint.pprint(y_values)

                        for t_range in t_values:
                            for y_range in y_values[0]:
                                ret[mode][uid].append([t_range[0], t_range[-1],
                                                       y_range[0], y_range[-1]])
                            for y_range in y_values[1]:
                                ret[mode][uid].append([t_range[0], t_range[-1],
                                                       y_range[0], y_range[-1]])

        return ret


    # --------------------------------------------------------------------------
    #
    def _consistency_state_model(self):

        ret = list()  # list of inconsistent entity IDs

        for et in self.list('etype'):

            self._rep.info('%s state model\n' % et)
            # sm = self.describe('state_model', etype=et)
            sv = self.describe('state_values', etype=et)[et]['state_values']

            for e in self.get(etype=et):

                es = e.states

                if not sv:
                    if es:
                        self._rep.warn('  %-30s : %s' % (et, list(es.keys())))
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
                for s in sv.values():

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


    # --------------------------------------------------------------------------
    #
    def tzero(self, t):
        '''
        Setting a `tzero` timestamp will shift all timestamps for all entities
        in this session by that amount.  This simplifies the alignment of
        multiple sessions, or the focus on specific events.
        '''

        old_tzero   = self._tzero
        self._tzero = t

        for entity in list(self._entities.values()):

            # entity.states are shallow copies of the events
            for event in entity.events:
                event[ru.TIME] += old_tzero
                event[ru.TIME] -= self._tzero


# ------------------------------------------------------------------------------

