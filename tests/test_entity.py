
import os
import json
import pytest
import radical.utils as ru
from radical.analytics.entity import Entity


# Test Directory use to load example json files
directory = "%s/example-data" % os.path.dirname(__file__)


# ------------------------------------------------------------------------------
#
@pytest.fixture
def pilot_entity():
    """Fixture to get the example Pilot entity from example data"""

    with open("%s/pilot-entity-example.json" % directory, 'r') as f:
        entity = json.load(f)
        entity['events'] = [tuple(event) for event in entity['events']]
        return entity


# ------------------------------------------------------------------------------
#
@pytest.fixture
def range_entity():
    """Fixture to get the example range-testing entity from example data"""

    with open("%s/range-testing-entity-example.json" % directory, 'r') as f:
        entity = json.load(f)
        entity['events'] = [tuple(event) for event in entity['events']]
        return entity


# ------------------------------------------------------------------------------
#
def get_states(events=None):
    """Get a dictionary of states from a list of event tuples"""

    ret_states = dict()
    if events is not None:
        for event in events:
            if event[ru.EVENT] == 'state':
                ret_states[event[ru.STATE]] = event

    return ret_states


# ------------------------------------------------------------------------------
#
def sort_events(events=None):
    """Sort a list of tuples of events"""

    ret_events = list()
    if events is not None:
        for event in sorted(events, key=lambda x: (x[ru.TIME])):
            ret_events.append(event)

    return ret_events


# ------------------------------------------------------------------------------
#
class TestEntity(object):

    # --------------------------------------------------------------------------
    #
    def test_t_start(self, pilot_entity):
        """Test a valid t_start"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])

        # Should match the time in the first element after sorting
        assert(e.t_start == events[0][ru.TIME])


    # --------------------------------------------------------------------------
    #
    def test_t_stop(self, pilot_entity):
        """Test a valid t_stop"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])

        # Should match the time in the last element after sorting
        assert(events[-1][ru.TIME] == e.t_stop)


    # --------------------------------------------------------------------------
    #
    def test_ttc(self, pilot_entity):
        """Test a valid ttc"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])

        # Should match the difference in time between
        # first and last elements after sorting
        assert(e.ttc == float(events[-1][ru.TIME] - events[0][ru.TIME]))


    # --------------------------------------------------------------------------
    #
    def test_t_range(self, pilot_entity):
        """Test a valid t_range"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])

        # Should match exactly what was passed in...
        assert[events[0][ru.TIME], events[-1][ru.TIME]] == e.t_range


    # --------------------------------------------------------------------------
    #
    def test_uid(self, pilot_entity):
        """Test a valid uid"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

        # Should match exactly what was passed in...
        assert(e.uid == pilot_entity['uid'])


    # --------------------------------------------------------------------------
    #
    def test_etype(self, pilot_entity):
        """Test a valid etype"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

        # Should match exactly what was passed in...
        assert(e.etype == pilot_entity['etype'])


    # --------------------------------------------------------------------------
    #
    def test_states(self, pilot_entity):
        """Test a valid states"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        # Get all events in the example file and put them in a dictionary
        states = get_states(pilot_entity['events'])

        # Should match a list of events of type 'state'
        # extracted from the events passed in
        assert(e.states == states)


    # --------------------------------------------------------------------------
    #
    def test_events(self, pilot_entity):
        """Test a valid events"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        # Get all events in order by timestamp
        events = sort_events(pilot_entity['events'])

        # Should match a list of sorted events (by the time field)
        # generated from the list of events passed in
        assert(e.events == events)


    # --------------------------------------------------------------------------
    #
    def test_description(self, pilot_entity):
        """Test a valid description"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

        # Should match exactly what was passed in...
        assert(type(e.description) is dict)
        assert(e.description == pilot_entity['details']['description'])


    # --------------------------------------------------------------------------
    #
    def test_cfg(self, pilot_entity):
        """Test a valid cfg"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

        # Should match exactly what was passed in...
        assert(type(e.cfg) is dict)
        assert(e.cfg == pilot_entity['details']['cfg'])


    # --------------------------------------------------------------------------
    #
    def test_consistency(self, pilot_entity):
        """Test a valid consistency"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

        # TODO: Better matching, for now we match just a dict()
        assert(type(e.consistency) is dict)


    # --------------------------------------------------------------------------
    #
    def test_as_dict(self, pilot_entity):
        """Test a valid as_dict"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        expected = {
            'uid': pilot_entity['uid'],
            'etype': pilot_entity['etype'],
            'states': get_states(pilot_entity['events']),
            'events': sort_events(pilot_entity['events'])
        }

        # Should match exactly what was passed in
        # as the order seen above...
        # don't match `cfg` and `description` as those are runtime dependent
        edict = e.as_dict()
        del(edict['cfg'])
        del(edict['description'])
        assert(edict == expected)


    ##############################################################
    # Test Ranges Method: expand=False, collapse=True
    #
    # We match range values form the example data at:
    #   ./example-data/range-testing-entity-example.json
    ##############################################################

    # --------------------------------------------------------------------------
    #
    def test_ranges_one_state(self, range_entity):
        """Test a valid ranges result with one state start/finish"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(state=['PMGR_ACTIVE_PENDING', 'FAILED'])
        assert(ranges == [[21.668299913406372, 50.227399826049805]])


    # --------------------------------------------------------------------------
    #
    def test_ranges_two_consecutive_state(self, range_entity):
        """Test a valid ranges result with two states start/finish"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two consecutive ranges which get collapsed to the spanning max
        ranges = e.ranges(state=[['NEW',            'PMGR_ACTIVE'     ],
                                 ['PMGR_LAUNCHING', 'PMGR_ACTIVE_PENDING']])
        assert(ranges == [[0.0, 4.449499845504761]])


    # --------------------------------------------------------------------------
    #
    def test_ranges_time_filter_exact_match(self, range_entity):
        """Test a valid ranges with time filter, exact matches"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # for state
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [21.668299913406372, 50.227399826049805]
        ])
        assert(ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        # for events
        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [4.446699857711792, 29.150099992752075]
        ])
        assert(ranges == [
            [4.446699857711792, 29.150099992752075]
        ])


    # --------------------------------------------------------------------------
    #
    def test_ranges_time_filter_no_match(self, range_entity):
        """Test a valid ranges with time filter, exact matches"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # for state
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [60.0, 70.0]
        ])
        assert(ranges == [])

        # for events
        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [30.0, 40.0]
        ])
        assert(ranges == [])


    # --------------------------------------------------------------------------
    #
    def test_ranges_time_filter_intersection_match(self, range_entity):
        """Test a valid ranges with time filter, one intersection match each"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # As you read the tests, here is what each symbol represents:
        #   [      ] --> matched range before time filtering
        #   {      } --> time filtering value
        #   (      ) --> matched range *after* time filtering

        # Inner intersection: [   {(  )}   ]
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [25.0, 30.0]
        ])
        assert(ranges == [
            [25.0, 30.0]
        ])

        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [5.0, 25.0]
        ])
        assert(ranges == [
            [5.0, 25.0]
        ])

        # Outter intersection: {   ([    ])   }
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [10.0, 60.0]
        ])
        assert(ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [0.0, 50.0]
        ])
        assert(ranges == [
            [4.446699857711792, 29.150099992752075]
        ])

        # Right-side intersection match: {   ([   )}   ]
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [25.0, 100.00]
        ])
        assert(ranges == [
            [25.0, 50.227399826049805]
        ])

        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [5.0, 50.0]
        ])
        assert(ranges == [
            [5.0, 29.150099992752075]
        ])

        # Left-side intersection match: [   {(   ])   }
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [0, 30.0]
        ])
        assert(ranges == [
            [21.668299913406372, 30.0]
        ])

        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [0.0, 25.0]
        ])
        assert(ranges == [
            [4.446699857711792, 25.0]
        ])


    # --------------------------------------------------------------------------
    #
    def test_ranges_multi_time_filter_exact_match(self, range_entity):
        """Test a valid ranges with multiple time filters,
        exact matches only"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # As you read the tests, here is what each symbol represents:
        #   [      ] --> matched range before time filtering
        #   {      } --> time filter #1
        #   |      | --> time filter #2
        #   (      ) --> matched range #1 *after* time filtering
        #   <      > --> matched range #2 *after* time filtering

        # Only one of the filters match: {([   ])}   |   |
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [21.668299913406372, 50.227399826049805],
            [60.0, 80.0]
        ])
        assert(ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [4.446699857711792, 29.150099992752075],
            [30.0, 40.0]
        ])
        assert(ranges == [
            [4.446699857711792, 29.150099992752075]
        ])

        # Only one of the filters match: {   }   |<[   ]>|
        ranges = e.ranges(state=[
            ['PMGR_ACTIVE_PENDING'],
            ['FAILED']
        ], time=[
            [60.0, 80.0],
            [21.668299913406372, 50.227399826049805]
        ])
        assert(ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'}],
            [{ru.EVENT: 'sync_rel'}]
        ], time=[
            [30.0, 40.0],
            [4.446699857711792, 29.150099992752075]
        ])
        assert(ranges == [
            [4.446699857711792, 29.150099992752075]
        ])


    # --------------------------------------------------------------------------
    #
    def test_ranges_multi_time_filter_intersection_match(
            self, range_entity):
        """Test a valid ranges with multiple time filters,
            intersection matches each"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        assert(e.t_start       ==  0)
        assert(e.t_stop        ==     50.507999897003174)
        assert(e.ttc           ==     50.507999897003174)
        assert(e.t_range       == [0, 50.507999897003174])
        assert(len(e.list_states()) ==  6)
        assert(len(e.states       ) ==  6)
        assert(len(e.events       ) == 22)
        # TODO: Add more assertions as needed

        # As you read the tests, here is what each symbol represents:
        #   [      ] --> matched range before time filtering
        #   {      } --> time filter #1
        #   |      | --> time filter #2
        #   (      ) --> matched range #1 *after* time filtering
        #   <      > --> matched range #2 *after* time filtering

        # Non-overlaping filters, one matches:    {([   )}   ]   |   |
        ranges = e.ranges(state=['PMGR_ACTIVE_PENDING', 'FAILED'],
                          time=[[21.668299913406372, 25.0], [60.0, 70.0]])
        assert(ranges == [[21.668299913406372, 25.0]])

        ranges = e.ranges(event=[{ru.EVENT: 'put'}, {ru.EVENT: 'sync_rel'}],
                          time=[[4.446699857711792, 15.0], [30.0, 50.0]
        ])
        assert(ranges == [[4.446699857711792, 15.0]])

        # Non-overlaping filters, both match: {   ([   )}   |<   ]>   |
        ranges = e.ranges(state=['PMGR_ACTIVE_PENDING', 'FAILED'],
                          time=[[10, 25.0], [30.0, 70.0]])
        assert(ranges == [[21.668299913406372, 25.0],
                           [30.0, 50.227399826049805]])

        ranges = e.ranges(event=[{ru.EVENT: 'put'}, {ru.EVENT: 'sync_rel'}],
                          time=[[0.0, 15.0], [20.0, 30.0]])
        assert(ranges == [[4.446699857711792, 15.0],
                           [20.0, 29.150099992752075]])

        # semi-overlaping filters, one matches: [   {(   ])   |   }   |
        ranges = e.ranges(state=['PMGR_ACTIVE_PENDING', 'FAILED'],
                          time=[[25.0, 70.0], [60.0, 80.0]])
        assert(ranges == [[25.0, 50.227399826049805]])

        ranges = e.ranges(event=[{ru.EVENT: 'put'}, {ru.EVENT: 'sync_rel'}],
                          time=[[15.0, 40.0], [30.0, 50.0]])
        assert(ranges == [[15.0, 29.150099992752075]])

        # semi-overlaping filters, both match: {   ([   |<   )}   ]>   |
        ranges = e.ranges(state=['PMGR_ACTIVE_PENDING', 'FAILED'],
                          time=[[10, 30.0], [25.0, 70.0]])
        assert(ranges == [[21.668299913406372, 50.227399826049805]])

        ranges = e.ranges(event=[{ru.EVENT: 'put'}, {ru.EVENT: 'sync_rel'}],
                          time=[[0.0, 20.0], [15.0, 30.0]])
        assert(ranges == [[4.446699857711792, 29.150099992752075]])

        # complete-overlap filters, both match: |   <[   {(   )}   ]>   |
        ranges = e.ranges(state=['PMGR_ACTIVE_PENDING', 'FAILED'],
                          time=[[25.0, 35.0], [10.0, 70.0]])
        assert(ranges == [[21.668299913406372, 50.227399826049805]])

        ranges = e.ranges(event=[{ru.EVENT: 'put'}, {ru.EVENT: 'sync_rel'}],
                          time=[[10.0, 20.0], [0.0, 30.0]])
        assert(ranges == [[4.446699857711792, 29.150099992752075]])


    # --------------------------------------------------------------------------
    #
    def test_ranges_two_overlaping_state(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two overlaping ranges
        ranges = e.ranges(state=[['NEW', 'PMGR_ACTIVE_PENDING'],
                                 ['PMGR_LAUNCHING', 'PMGR_ACTIVE']])
        assert(ranges == [[4.433599948883057, 4.449499845504761]])


    # --------------------------------------------------------------------------
    #
    def test_ranges_one_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[
            ({ru.EVENT: 'put'}),
            ({ru.EVENT: 'cmd'})
        ])
        assert(ranges == [
            [4.446699857711792, 50.507999897003174]
        ])


    # --------------------------------------------------------------------------
    #
    def test_ranges_one_event_multi_match(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[
            ({ru.EVENT: 'update_request'}),
            ({ru.EVENT: 'update_pushed'})
        ])
        assert(ranges == [
            [4.447200059890747 , 4.457900047302246],
            [4.458099842071533 , 5.236199855804443],
            [21.666899919509888, 21.685499906539917],
            [29.752099990844727, 29.939599990844727],
            [30.722899913787842, 32.28690004348755 ],
            [50.22889995574951 , 50.240999937057495]
        ])


    # --------------------------------------------------------------------------
    #
    def test_ranges_two_consecutive_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two consecutive ranges
        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'     }, {ru.EVENT: 'hostname'}],
            [{ru.EVENT: 'sync_rel'}, {ru.EVENT: 'cmd'     }]
        ])
        print(ranges)
        assert(ranges == [[4.446699857711792, 29.150099992752075],
                          [29.760799884796143, 50.507999897003174]])


    # --------------------------------------------------------------------------
    #
    def test_ranges_two_overlaping_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # FIXME: this is the same test as above

        # Two overlaping ranges
        ranges = e.ranges(event=[
            [{ru.EVENT: 'put'     }, {ru.EVENT: 'hostname'}],
            [{ru.EVENT: 'sync_rel'}, {ru.EVENT: 'cmd'     }]
        ])
        assert(ranges == [
            [4.446699857711792, 29.150099992752075],
            [29.760799884796143, 50.507999897003174]
        ])


    # --------------------------------------------------------------------------
    #
    def test_empty_profile(self, pilot_entity):

        with pytest.raises(Exception):
            Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=list(),
                   _details=pilot_entity['details'])


    # --------------------------------------------------------------------------
    #
    def test_empty_details(self, pilot_entity):

        with pytest.raises(Exception):
            Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=dict())



    ##############################################################
    # Test invalid scenarios
    ##############################################################

    # --------------------------------------------------------------------------
    #
    def test_none_uid(self, pilot_entity):

        with pytest.raises(Exception):
            Entity(_uid=None,
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )


    # --------------------------------------------------------------------------
    #
    def test_none_etype(self, pilot_entity):

        Entity(_uid=pilot_entity['uid'],
               _etype=None,
               _profile=pilot_entity['events'],
               _details=pilot_entity['details']
               )


    # --------------------------------------------------------------------------
    #
    def test_none_profile(self, pilot_entity):
        with pytest.raises(Exception):
            Entity(_uid=None,
                   _etype=pilot_entity['etype'],
                   _profile=None,
                   _details=pilot_entity['details']
                   )


    # --------------------------------------------------------------------------
    #
    def test_none_details(self, pilot_entity):
        with pytest.raises(Exception):
            Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=None
                   )


    # --------------------------------------------------------------------------
    #
    def test_invalid_ranges_no_end_matched_state(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[({ru.EVENT: 'put'}), ({ru.EVENT: 'aaa'})
        ])
        assert(ranges == [])


    # --------------------------------------------------------------------------
    #
    def test_invalid_ranges_no_end_matched_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[('NEW'), ('AAA') ])
        assert(ranges == [])


    # --------------------------------------------------------------------------
    #
    def test_invalid_ranges_no_start_matched_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[({ru.EVENT: 'aaa'}), ({ru.EVENT: 'put'})
        ])
        assert(ranges == [])


    # --------------------------------------------------------------------------
    #
    def test_invalid_ranges_no_start_matched_state(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[('AAA'), ('NEW')])
        assert(ranges == [])


# ------------------------------------------------------------------------------

