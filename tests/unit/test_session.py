__copyright__ = 'Copyright 2014-2016, http://radical.rutgers.edu'
__license__   = 'MIT'

import pytest

import radical.analytics as ra

def test_get_sid_no_src():
    sid = None
    src = '/dev/null/nodir'
    s = ra.Session()
    with pytest.raises(SystemExit):
        s._get_sid(sid, src)

def test_get_sid_src_is_dir(tmpdir):
    sid = None
    src = tmpdir
    s = ra.Session()
    sid, src, tgt, ext = s._get_sid(sid, src)
    assert sid == ''

def test_get_sid_src_is_file_prof():
    assert True

def test_get_sid_src_is_file_tgz():
    assert True

def test_get_sid_src_is_file_tbz():
    assert True

def test_get_sid_src_is_file_tbz2():
    assert True

def test_get_sid_src_is_file_tar.gz():
    assert True

def test_get_sid_src_is_file_tar.bz():
    assert True

def test_get_sid_src_is_file_tar.bz2():
    assert True

def test_get_sid_src_is_file_unknown():
    sid = None
    src = 'srcfile.noext'
    s = ra.Session()
    with pytest.raises(SystemExit):
        s._get_sid(sid, src)

def test_get_sid_sid_notnull.bz2():
    assert True

def test_get_sid_sid_wellformed.bz2():
    assert True
