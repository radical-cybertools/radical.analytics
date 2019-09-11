
  - For a list of bug fixes, see
    https://github.com/radical-cybertools/radical.analytics/issues?q=is%3Aissue+is%3Aclosed+sort%3Aupdated-desc
  - For a list of open issues and known problems, see
    https://github.com/radical-cybertools/radical.analytics/issues?q=is%3Aissue+is%3Aopen+


0.70.0 Release                                                        2019-07-07
--------------------------------------------------------------------------------

  - plot improvements
  - fix tarball handling


0.60.1 Hotfix                                                         2019-05-28
--------------------------------------------------------------------------------

  - fix deployement dependency (thanks Matteo!)


0.60.0 Release                                                        2019-04-10
--------------------------------------------------------------------------------

  - fail on and mark missing mandatory events
  - add a native radical.analytics session (#63)
  - add events to capture pre-exec durations (#67)
  - add consistency check
  - add allocation plot script
  - add figure size option
  - add plotting class
  - add concurrency plot
  - add statistics
  - add utilization plot
  - example fixes
  - fix issue (#74)
  - fix logger creation
  - fix prints in wrangler
  - apply coding guidelines


0.50.4 Release                                                        2018-12-20
--------------------------------------------------------------------------------

  - make pypi happy


0.50.3 Release                                                        2018-12-19
--------------------------------------------------------------------------------

  - fix license inconsistency


0.50.2 Release                                                        2018-12-19
--------------------------------------------------------------------------------

  - add license file


0.50.1 Release                                                        2018-11-20
--------------------------------------------------------------------------------

  - fixes to EnTK integration


0.50.0 Release                                                        2018-08-20
--------------------------------------------------------------------------------

  - support sessions which only have profiles, but a limited or no event or
    state model

  
  
0.47 Release                                                          2017-11-19
--------------------------------------------------------------------------------

  - Adding plotting class
  - add concurrency plot
  - PR #41
  - If ranges is empty do nothing, else update dict.
    Value of dict is a list of lists in case there are more than one ranges
  - Single session, multiple pilots utilization
  - TTC diagrams
  - Utilization method. For the moment single RP session, single pilot
  - add several examples
  - add time filter tests
  - add valid range testing
  - adding test case for the magic function -- currently test fails for dataset
    with execution barrier
  - behave on empty event queries
  - better testing for time filters
  - entk integration
  - entity.ranges() *always* returns a list
  - event profiling cleanup
  - expose session id
  - expose stats, new event type
  - ignore gitignore
  - import matplotlib only if needed, to avoid hard dependency
  - keep up with RU changes
  - make sure we get session ID from an experiment dir
  - mocking tests file structure, better .gitignore
  - owner and consumer are mandatory inputs in the API call
  - remove unwanted files
  - support tarballs tarballs: those named "sid.tbz" etc. are now transparently
    unpacked and used.
  - testing ranges
  - tests require pytest
  - use empty range set and "None" to indicate condition mismatch
  - work on RA memory consumption


0.45 Release                                                          2017-02-28
--------------------------------------------------------------------------------

  - clean out repository
  - sync branches
  - sync version across radical stack


0.1  Release                                                          2016-02-20
--------------------------------------------------------------------------------

  - initial release


--------------------------------------------------------------------------------

