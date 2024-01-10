
- For a list of bug fixes, see:
    <https://github.com/radical-cybertools/radical.analytics/issues?q=is%3Aissue+is%3Aclosed+sort%3Aupdated-desc>
- For a list of open issues and known problems, see:
    <https://github.com/radical-cybertools/radical.analytics/issues?q=is%3Aissue+is%3Aopen>


1.42.0 Release                                                        2024-01-10
--------------------------------------------------------------------------------

  - maintenance


1.42.0 Release                                                        2023-12-04
--------------------------------------------------------------------------------

  - added check for `re.Pattern`
  - create experiments from session sources and instances
  - fixed concurrency offset
  - improve filter semantics


1.41.0 Release                                                        2023-10-17
--------------------------------------------------------------------------------

  - fix RTD
  - Add long description for pypi


1.34.0 Release                                                        2023-06-22
--------------------------------------------------------------------------------

  - consistency across RCT modules


1.33.0 Release                                                        2023-04-25
--------------------------------------------------------------------------------

  - avoid hardcoding session IDs
  - enable compilation of notebooks
  - fix extension renaming
  - Iterate and fix all the tutorials
  - simplify session ingest
  - use same ncores/gpus of frontier


1.20.1 Release                                                        2022-12-16
--------------------------------------------------------------------------------

  - fix MANIFEST.in


1.20.0 Release                                                        2022-12-16
--------------------------------------------------------------------------------

  - re-enable notebooks
  - fix doc deps
  - fix rtd build
  - remove invalid assert
  - remove outdated test
  - sync with ru


1.18.0 Release                                                        2022-10-11
--------------------------------------------------------------------------------

  - better sorting for state transition plots
  - documentation for plot_util_2, fix transition events
  - better etype guessing
  - raptor tasks use normal task events now (`rank_*`)
  - separate raptor contributions to utilization plots
  - sync ci workflow and linter settings


1.16.0 Release                                                        2022-08-15
--------------------------------------------------------------------------------

  - use https instead of git for doc requirements


1.14.0 Release                                                        2022-04-13
--------------------------------------------------------------------------------

  - get cores_per_node from rm_info
  - handle session w/o bootstrap events


1.13.0 Release                                                        2022-03-21
--------------------------------------------------------------------------------

  - add badges and links
  - adding requirements
  - documentation fixes (layout and content, notbeook based examples)
  - support concurrency analysis
  - convert all the protected char in latex
  - remove debug prints
  - remove outdated code
  - stringent check for non-negative times
  - timestamp analysis
  - rename `unit` to `task`
  

1.6.7 Release                                                         2021-07-08
--------------------------------------------------------------------------------

- utils/plot.py: help functions for plotting with Matplotlib
- style/radical_mpl.txt: default Matplotlib style for publication-grade plots.
- Separate type of resources (e.g., 'cpu', 'gpu) in resource utilization plot
- New utilization plot. aggregated utilization to improve performance and scale
- Documentation: Resource utilization, renaming compute unit -> task
- Tools: bin/rp_inspect/*.py plot 4 metrics for RP sessions
- Various bug fixes

1.5.0 Release                                                         2020-08-04
--------------------------------------------------------------------------------

- Move to Python 3
- Fix multiple bugs
- Align with release number of RCT stack
- Linting and RCT best code practices
- New documentation

0.72.1 Hotfix Release                                                 2019-09-28
--------------------------------------------------------------------------------

- fix #102

0.72.0 Release                                                        2019-09-11
--------------------------------------------------------------------------------

- introduce analytics.Experiment class and move utilization method to it
- sessions are now cached
- Expand upon modeling TTX
- TTC diagrams
- add jsrun version of metrics
- add quick plotter script
- documentation
- entity.ranges() *always* returns a list
- experiment level utilization plots
- fix off-by-one error
- increase timer precision
- re-align utilization plot with pilot runtime
- recursive profiles for RA sessions
- support bz2
- support global session time shift (session.tzero)

0.70.0 Release                                                        2019-07-07
--------------------------------------------------------------------------------

- plot improvements
- fix tarball handling

0.60.1 Hotfix                                                         2019-05-28
--------------------------------------------------------------------------------

- fix deployment dependency (thanks Matteo!)

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

- support sessions which only have profiles, but a limited or no event or state model

0.47 Release                                                          2017-11-19
--------------------------------------------------------------------------------

- Adding plotting class
- add concurrency plot
- PR #41
- If ranges is empty do nothing, else update dict. Value of dict is a list of lists in case there are more than one ranges
- Single session, multiple pilots utilization
- TTC diagrams
- Utilization method. For the moment single RP session, single pilot
- add several examples
- add time filter tests
- add valid range testing
- adding test case for the magic function -- currently test fails for dataset with execution barrier
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
- support tarballs tarballs: those named "sid.tbz" etc. are now transparently unpacked and used.
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

