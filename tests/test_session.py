import os
import json
import pytest
import radical.utils as ru
from radical.analytics import Session


# Test Directory use to load example json files
directory = "{}/example-data".format(
    os.path.dirname(os.path.abspath(__file__)))

class TestSession(object):

    def test_example(self):
        """do some test here"""
        assert True
