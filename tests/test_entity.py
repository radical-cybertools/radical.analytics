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
    with open("{}/pilot-entity-example.json".format(directory), 'r') as f:
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

    def test_valid_t_start(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert events[0][ru.TIME] == e.t_start

    def test_valid_t_stop(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert events[-1][ru.TIME] == e.t_stop

    def test_valid_ttc(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert float(events[-1][ru.TIME] - events[0][ru.TIME]) == e.ttc

    def test_valid_t_range(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        events = sort_events(pilot_entity['events'])
        assert [events[0][ru.TIME], events[-1][ru.TIME]] == e.t_range

    def test_valid_uid(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (e.uid == pilot_entity['uid'])

    def test_valid_etype(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (e.etype == pilot_entity['etype'])

    def test_valid_states(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        # Get all events in the example file and put them in a dictionary
        states = get_states(pilot_entity['events'])
        assert (e.states == states)

    def test_valid_events(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        # Get all events in order by timestamp
        events = sort_events(pilot_entity['events'])
        assert (e.events == events)

    def test_valid_description(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (type(e.description) is dict)
        assert (e.description == pilot_entity['details']['description'])

    def test_valid_cfg(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (type(e.cfg) is dict)
        assert (e.cfg == pilot_entity['details']['cfg'])

    def test_valid_consistency(self, pilot_entity):
        e = Entity(_uid=pilot_entity['uid'],
                   _etype=pilot_entity['etype'],
                   _profile=pilot_entity['events'],
                   _details=pilot_entity['details']
                   )
        assert (type(e.consistency) is dict)

    def test_valid_as_dict(self, pilot_entity):
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
