
  - For a list of bug fixes, see 
    https://github.com/radical-cybertools/radical.analytics/issues?q=is%3Aissue+is%3Aclosed+sort%3Aupdated-desc
  - For a list of open issues and known problems, see
    https://github.com/radical-cybertools/radical.analytics/issues?q=is%3Aissue+is%3Aopen+


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

