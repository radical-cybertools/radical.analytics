import os
import json
import pytest
import radical.utils as ru
from radical.analytics.entity import Entity


# Test Directory use to load example json files
directory = "{}/example-data".format(
    os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def pilot_entity():
    """Fixture to get the example Pilot entity"""
    with open(
            "{}/pilot-entity-example.json".format(directory),
            'r') as f:
        entity = json.load(f)
        entity['events'] = [tuple(l) for l in entity['events']]
        return entity


@pytest.fixture
def range_entity():
    """Fixture to get the example range-testing entity"""
    with open(
            "{}/range-testing-entity-example.json".format(directory),
            'r') as f:
        entity = json.load(f)
        entity['events'] = [tuple(l) for l in entity['events']]
        return entity


def get_states(events=None):
    """Get a dictionary of states from a list of event tuples"""
    ret_states = dict()
    if events is not None:
        for event in events:
            if event[ru.EVENT] == 'state':
                ret_states[event[ru.STATE]] = event
    return ret_states


def sort_events(events=None):
    """Sort a list of tuples of events"""
    ret_events = list()
    if events is not None:
        for event in sorted(events, key=lambda (x): (x[ru.TIME])):
            ret_events.append(event)
    return ret_events


class TestEntity(object):

    def test_t_start(self, pilot_entity):
        """Test a valid t_start"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert events[0][ru.TIME] == e.t_start

    def test_t_stop(self, pilot_entity):
        """Test a valid t_stop"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert events[-1][ru.TIME] == e.t_stop

    def test_ttc(self, pilot_entity):
        """Test a valid ttc"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert float(events[-1][ru.TIME] - events[0][ru.TIME]) == e.ttc

    def test_t_range(self, pilot_entity):
        """Test a valid t_range"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert [events[0][ru.TIME], events[-1][ru.TIME]] == e.t_range

    def test_uid(self, pilot_entity):
        """Test a valid uid"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (e.uid == pilot_entity['uid'])

    def test_etype(self, pilot_entity):
        """Test a valid etype"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (e.etype == pilot_entity['etype'])

    def test_states(self, pilot_entity):
        """Test a valid states"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        # Get all events in the example file and put them in a dictionary
        states = get_states(pilot_entity['events'])
        assert (e.states == states)

    def test_events(self, pilot_entity):
        """Test a valid events"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        # Get all events in order by timestamp
        events = sort_events(pilot_entity['events'])
        assert (e.events == events)

    def test_description(self, pilot_entity):
        """Test a valid description"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (type(e.description) is dict)
        assert (e.description == pilot_entity['details']['description'])

    def test_cfg(self, pilot_entity):
        """Test a valid cfg"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (type(e.cfg) is dict)
        assert (e.cfg == pilot_entity['details']['cfg'])

    def test_consistency(self, pilot_entity):
        """Test a valid consistency"""
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (type(e.consistency) is dict)

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
        assert (e.as_dict() == expected)

##########################################
# Test Ranges: expand=False, collapse=True
##########################################

    def test_ranges_one_state(self, range_entity):
        """Test a valid ranges result with one state in/out"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ])
        assert (ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

    def test_ranges_two_consecutive_state(self, range_entity):
        """Test a valid ranges result with two states in/out"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two consecutive ranges
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE', 'PMGR_LAUNCHING'),
            ('NEW', 'PMGR_ACTIVE_PENDING')
        ])
        assert (ranges == [
            [0.0, 4.433599948883057],
            [4.449499845504761, 21.668299913406372]
        ])

    def test_ranges_time_filter_exact_match(self, range_entity):
        """Test a valid ranges with time filter, exact matches"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # states
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (21.668299913406372, 50.227399826049805)
        ])
        assert (ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        # events
        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (4.446699857711792, 29.150099992752075)
        ])
        assert (ranges == [
            [4.446699857711792, 29.150099992752075]
        ])

    def test_ranges_time_filter_intersection_match(self, range_entity):
        """Test a valid ranges with time filter, one intersection match each"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )
        # Inner
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (25.0, 30.0)
        ])
        assert (ranges == [
            [25.0, 30.0]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (5.0, 25.0)
        ])
        assert (ranges == [
            [5.0, 25.0]
        ])

        # Outter
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (10.0, 60.0)
        ])
        assert (ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (0.0, 50.0)
        ])
        assert (ranges == [
            [4.446699857711792, 29.150099992752075]
        ])

        # Right Match
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (25.0, 100.00)
        ])
        assert (ranges == [
            [25.0, 50.227399826049805]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (5.0, 50.0)
        ])
        assert (ranges == [
            [5.0, 29.150099992752075]
        ])

        # Left match
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (0, 30.0)
        ])
        assert (ranges == [
            [21.668299913406372, 30.0]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (0.0, 25.0)
        ])
        assert (ranges == [
            [4.446699857711792, 25.0]
        ])

    def test_ranges_multi_time_filter_exact_match(self, range_entity):
        """Test a valid ranges with multiple time filters,
        exact matches only"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (0, 20.0), (21.668299913406372, 50.227399826049805)
        ])
        assert (ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (0.0, 4.0), (4.446699857711792, 29.150099992752075)
        ])
        assert (ranges == [
            [4.446699857711792, 29.150099992752075]
        ])

    def test_ranges_multi_time_filter_intersection_match(
            self, range_entity):
        """Test a valid ranges with multiple time filters,
            intersection matches each"""
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Outer
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (10, 25.0), (20.0, 70.0)
        ])
        assert (ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (0.0, 4.0), (0.0, 30.00)
        ])
        assert (ranges == [
            [4.446699857711792, 29.150099992752075]
        ])

        # Inner
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (25.0, 30.0), (10.0, 60.0)
        ])
        assert (ranges == [
            [25.0, 30.0]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (5.0, 25.0), (0.0, 30.00)
        ])
        assert (ranges == [
            [5.0, 25.0]
        ])

        # Right
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (25.0, 60.0), (10.0, 60.0)
        ])
        assert (ranges == [
            [25.0, 50.227399826049805]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (5.0, 30.0), (0.0, 30.00)
        ])
        assert (ranges == [
            [5.0, 29.150099992752075]
        ])

        # Left
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE_PENDING'),
            ('FAILED')
        ], time=[
            (10, 30.0), (10.0, 60.0)
        ])
        assert (ranges == [
            [21.668299913406372, 50.227399826049805]
        ])

        ranges = e.ranges(events=[
            ({ru.STATE: 'put'}),
            ({ru.STATE: 'sync_rel'})
        ], time=[
            (0.0, 25.0), (0.0, 30.00)
        ])
        assert (ranges == [
            [4.446699857711792, 25.0]
        ])

    def test_ranges_two_overlaping_state(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two overlaping ranges
        ranges = e.ranges(state=[
            ('PMGR_ACTIVE', 'NEW'),
            ('PMGR_LAUNCHING', 'PMGR_ACTIVE_PENDING')
        ])
        assert (ranges == [
            [0.0, 4.433599948883057]
        ])

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
        assert (ranges == [
            [4.446699857711792, 50.507999897003174]
        ])

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
        assert (ranges == [
            [4.447200059890747, 4.457900047302246],
            [4.458099842071533, 5.236199855804443],
            [21.666899919509888, 21.685499906539917],
            [29.752099990844727, 29.939599990844727],
            [30.722899913787842, 32.28690004348755],
            [50.22889995574951, 50.240999937057495]
        ])

    def test_ranges_two_consecutive_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two consecutive ranges
        ranges = e.ranges(event=[
            ({ru.EVENT: 'put'}, {ru.EVENT: 'hostname'}),
            ({ru.EVENT: 'sync_rel'}, {ru.EVENT: 'cmd'})
        ])
        assert (ranges == [
            [4.446699857711792, 29.150099992752075],
            [29.760799884796143, 50.507999897003174]
        ])

    def test_ranges_two_overlaping_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Two overlaping ranges
        ranges = e.ranges(event=[
            ({ru.EVENT: 'put'}, {ru.EVENT: 'hostname'}),
            ({ru.EVENT: 'sync_rel'}, {ru.EVENT: 'cmd'})
        ])
        assert (ranges == [
            [4.446699857711792, 29.150099992752075],
            [29.760799884796143, 50.507999897003174]
        ])

    def test_empty_profile(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=list(),
                   _details=pilot_entity['details']
                   )
        assert (e.t_start == 0)
        assert (e.t_stop == 0)
        assert (e.ttc == 0)
        assert (e.t_range == [0, 0])
        assert (e.states == dict())
        assert (e.events == list())
        assert (e.list_states() == list())
        # TODO: Add more assetions as needed

    def test_empty_details(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=dict()
                   )

        assert (e.cfg == dict())
        assert (e.description == dict())
        # TODO: Add more assetions as needed / fix assertions

##########################################
# Test Invalid Scenarios
##########################################
    def test_none_uid(self, pilot_entity):
        with pytest.raises(Exception):
            Entity(_uid=None,
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

    def test_none_etype(self, pilot_entity):
        with pytest.raises(Exception):
            Entity(_uid=pilot_entity['uid'],
                   _etype=None,
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )

    def test_none_profile(self, pilot_entity):
        with pytest.raises(Exception):
            Entity(_uid=None,
                   _etype=pilot_entity['etype'],
                   _profile=None,
                   _details=pilot_entity['details']
                   )

    def test_none_details(self, pilot_entity):
        with pytest.raises(Exception):
            Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=None
                   )

    def test_invalid_ranges_no_end_matched_state(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[
            ({ru.EVENT: 'put'}),
            ({ru.EVENT: 'aaa'})
        ])
        assert (ranges == [])

    def test_invalid_ranges_no_end_matched_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[
            ('NEW'),
            ('AAA')
        ])
        assert (ranges == [])

    def test_invalid_ranges_no_start_matched_state(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[
            ({ru.EVENT: 'aaa'}),
            ({ru.EVENT: 'put'})
        ])
        assert (ranges == [])

    def test_invalid_ranges_no_start_matched_event(self, range_entity):
        e = Entity(_uid=range_entity['uid'],
                   _etype=range_entity['etype'],
                   _profile=range_entity['events'],
                   _details=range_entity['details']
                   )

        # Only one range of one start/end
        ranges = e.ranges(event=[
            ('AAA'),
            ('NEW')
        ])
        assert (ranges == [])
