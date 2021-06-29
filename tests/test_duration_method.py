
# import radical.analytics as ra
import radical.pilot as rp
# import os
# import glob


# ------------------------------------------------------------------------------
#
def get_duration_ra(session):

    '''
    Get duration using the 'duration' method of the session object in analytics
    '''
    units = session.filter(etype='unit', inplace=False)
    return units.duration([rp.UMGR_SCHEDULING_PENDING, rp.DONE])


# ------------------------------------------------------------------------------
#
def get_duration_minmax(session):

    '''
    Get max of the final state and min of the initial state for all units
    '''

    # FIXME: this is a useless test - semantically it tests if
    #        ru.collapse_ranges maintains time ordering, which should be tested
    #        in RU, not here.  Also, it will fail for partitioned ranges, so
    #        will not work for all test cases.

    units_1  = session.get(state=rp.UMGR_SCHEDULING_PENDING, etype='unit')
    start_rp = [unit.states[rp.UMGR_SCHEDULING_PENDING]['time']
                            for unit in units_1]

    units_2  = session.get(state=rp.DONE, etype='unit')
    stop_rp = [unit.states[rp.DONE]['time'] for unit in units_2]

    return max(stop_rp) - min(start_rp)


# ------------------------------------------------------------------------------
#
def collapse_ranges(ranges):
    """
    given be a set of ranges (as a set of pairs of floats [start, end] with
    'start <= end'. This algorithm will then collapse that set into the
    smallest possible set of ranges which cover the same, but not more nor
    less, of the domain (floats).

    We first sort the ranges by their starting point. We then start with the
    range with the smallest starting point [start_1, end_1], and compare to
    the next following range [start_2, end_2], where we now know that
    start_1 <= start_2. We have now two cases:

    a) when start_2 <= end_1, then the ranges overlap, and we collapse them
    into range_1: range_1 = [start_1, max[end_1, end_2]

    b) when start_2 > end_2, then ranges don't overlap. Importantly, none of
    the other later ranges can ever overlap range_1. So we move range_1 to
    the set of final ranges, and restart the algorithm with range_2 being
    the smallest one.

    Termination condition is if only one range is left -- it is also moved
    to the list of final ranges then, and that list is returned.
    """

    # FIXME: this is a useless helper: it implements ru.collapse_ranges
    #        again, and of course the same result appears - duh! We can
    #        rely external methods to be tested.

    final = []

    # sort ranges into a copy list
    _ranges = sorted (ranges, key=lambda x: x[0])

    START = 0
    END = 1

    base = _ranges[0]  # smallest range

    for _range in _ranges[1:]:

        if _range[START] <= base[END]:

            # ranges overlap -- extend the base
            base[END] = max(base[END], _range[END])

        else:

            # ranges don't overlap -- move base to final, and current _range
            # becomes the new base
            final.append(base)
            base = _range

    # termination: push last base to final
    final.append(base)

    return final


# ------------------------------------------------------------------------------
#
def get_duration_ru(session):

    '''
    Use the sliding window method in radical.utils to derive the duration
    between the two states for all units
    '''

    # FIXME: This is a useless test: it implements ra.session.duration again and
    #        checks if it jields the same result.  Duh, what else could happen?

    units  = session.get(state=[rp.UMGR_SCHEDULING_PENDING, rp.DONE],
                         etype='unit')

    ranges = [[unit.states[rp.UMGR_SCHEDULING_PENDING]['time'],
               unit.states[rp.DONE                   ]['time']]
              for unit in units]

    overlap = 0.0
    for crange in collapse_ranges(ranges):
        overlap += crange[1] - crange[0]

    return overlap


# ------------------------------------------------------------------------------
#
def test_duration_no_barrier():

    '''
    This function tests if the durations obtained from the analytics function is
    the same as the duration obtained by the utils function. They should both be
    equal to the 'max-min' (of the FINAL and INITIAL states respectively) as the
    data set in this case consists of profiles when all units are concurrently
    being executed, i.e. there is no execution barrier between them and thus no
    'gap'/full overlap.
    '''

    # FIXME: data files broken
    return

    # data_loc   = '%s/no_barrier_data' % os.path.dirname(__file__)
    # json_files = glob.glob('%s/*.json' % data_loc)
    # json_file  = json_files[0]
    # sid        = os.path.basename(json_file)[:-5]

    # session = ra.Session(sid=sid, stype='radical.pilot', src=data_loc)

    # assert get_duration_ra(session) == get_duration_ru(session)
    # assert get_duration_ra(session) == get_duration_minmax(session)


# ------------------------------------------------------------------------------
#
def test_duration_method_barrier():

    '''
    This function tests if the durations obtained from the analytics function is
    the same as the duration obtained by the utils function. They should both be
    less than the 'max-min' (of the FINAL and INITIAL states respectively) as
    the data set in this case consists of profiles when not all units are
    concurrently being executed, i.e. there is an execution barrier between them
    and thus a 'gap' between their executions.
    '''

    # FIXME: data files broken
    return

    # data_loc   = '%s/barrier_data' % os.path.dirname(__file__)
    # json_files = glob.glob('%s/*.json' % data_loc)
    # json_file  = json_files[0]
    # sid        = os.path.basename(json_file)[:-5]

    # session = ra.Session(sid=sid, stype='radical.pilot', src=data_loc)

    # assert get_duration_ra(session) == get_duration_ru(session)
    # assert get_duration_ra(session) <  get_duration_minmax(session)


# ------------------------------------------------------------------------------

