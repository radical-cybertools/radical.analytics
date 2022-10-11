import os
import sys
import glob
import functools
import pandas as pd
import matplotlib as mpl
import radical.utils as ru


# ------------------------------------------------------------------------------
#
def get_plotsize(width, fraction=1, subplots=(1, 1)):
    """ Sets aesthetic figure dimensions to avoid scaling in latex.

    Parameters
    ----------
    width   : float
              Width in points (pts).
    fraction: float
              Fraction of the width which you wish the figure to occupy.
    subplots: tuple
              Number of raws and number of columns of the plot.

    Returns
    -------
    fig_dim : tuple
              Dimensions of figure in inches.
    """
    # Width of figure
    fig_width_pt = width * fraction

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    golden_ratio = (5 ** 0.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt

    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return fig_width_in, fig_height_in


# ------------------------------------------------------------------------------
#
def get_mplstyle(name):
    """Returns the installation path of a Matplotlib style.

    Parameters
    ----------
    name: string
          Filename ending in .txt.

    Returns
    -------
    path : string
           Normalized path.
    """

    path  = os.path.dirname(sys.executable)
    path += '/../share/radical.analytics/styles'

    for path in glob.glob('%s/*.txt' % path):
        if path.endswith('/%s.txt' % name):
            return os.path.normpath(path)


    raise RuntimeError('style %s not found' % name)


# ------------------------------------------------------------------------------
#
def stack_transitions(series, tresource, to_stack):
    '''Creates data frames for each metric and combines them into one data frame
    for alignment. Since transitions obviously happen at arbitrary times, the
    timestamps for metric A may see no transitions for metric B. When using a
    combined timeline, we end up with NaN entries for some metrics on most
    timestamp, which in turn leads to gaps when plotting. So we fill the NaN
    values with the previous valid value, which in our case holds until the next
    transition happens.

    Parameters
    ----------
    series   : dict
               Pairs of timestamps for each metric of each type of
               resource. E.g. series['cpu']['term'] = [[0.0, 0.0],
               [302.4374113082886, 100.0], [304.6761999130249, 0.0]].
    tresource: string
               Type of resource. E.g., 'cpu' or 'gpu'.

    to_stack : list
               List of metrics to stack. E.g., ['bootstrap', 'exec_cmd',
               'schedule', 'exec_rp', 'term', 'idle'].

    Returns
    -------
    stacked : pandas.DataFrame
              Columns: time and one for each metric. Rows: timestamp and
              percentage / amount of resource utilization for each metric at
              that point in time.
    '''

    dfs = [pd.DataFrame(series[tresource][m], columns=['time', m])
            for m in series[tresource]]

    # merge them into one data frame, creating a common time-line
    merged = functools.reduce(lambda left, right:
                                     pd.merge(left, right,
                                              left_on='time',
                                              right_on='time',
                                              how='outer'), dfs)
    # sort the global time line
    merged.sort_values(by='time', inplace=True)

    # fill in missing values (carry over previous ones)
    merged.fillna(method='ffill', inplace=True)

    # stacked plotting and area filling don't play well together in matplotlib.
    # Instead we use normal (unstacked) plot routines and fill in between, we
    # manually compute the stacked numbers: copy the timeline to a new data
    # frame.
    stacked = merged[['time']].copy()
    prev    = list()

    # for each metric, copy the metric column and add all previous columns
    for m in to_stack:
        stacked[m] = merged[m]
        for p in prev:
            stacked[m] += merged[p]
        prev.append(m)

    return stacked


# ------------------------------------------------------------------------------
#
def get_pilot_series(session, pilot, tmap, resrc, percent=True):
    """ Derives the series of pilot resource transition points from the metrics.

    Parameters
    ----------
    session: ra.Session
             The Session object of RADICAL-Analytics created from a RCT sandbox.
    pilot  : ra.Entity
             The pilot object of session.
    tmap   : dict
             Map events to transition points in which a metric changes its
             owner. E.g., [{1: 'bootstrap_0_start'}, 'system', 'bootstrap']
             defines bootstrap_0_start as the event in which resources pass
             from the system to the bootstrapper.
    resrc  : list
             Type of resources. E.g., ['cpu', 'gpu'].
    percent: bool
             Whether we want to return resource utilization as percentage of
             the total resources available or as count of a type of resource.

    Returns
    -------
    p_resrc: dict
             Amount of resources in the pilot.
    series : dict
             List of time series per metric and resource type. E.g.,
             series['cpu']['term'] = [[0.0, 0.0], [302.4374113082886, 100.0],
             [304.6761999130249, 0.0]].
    x      : dict
             Mix and max value of the X-axes.

    """

    # get total pilot resources and runtime,
    p_resrc = {'cpu': pilot.cfg['cores'],
               'gpu': pilot.cfg['gpus' ]}

    t_min = None
    t_max = None

    try   : t_min = pilot.timestamps(event={1: 'bootstrap_0_start'})[0]
    except: pass

    try   : t_max = pilot.timestamps(event={1: 'bootstrap_0_stop'})[0]
    except: pass

    # fallback for missing bootstrap events
    if t_min is None: t_min = pilot.timestamps(state='PMGR_ACTIVE')[0]
    if t_max is None: t_max = pilot.events[-1][ru.TIME]

    assert t_min is not None
    assert t_max is not None

    t_span = t_max - t_min
    x_min  = 0
    x_max  = t_span + 0.05 * t_span

    # derive the pilot resource transition points from the metrics. Metrics
    # might be pulled from rp.utils but should be consistent with those used for
    # RU v.1.
    # rpp = rp.utils.prof_utils

    # get all contributions
    metrics = list()
    for trans in tmap.values():
        metrics += [x[1] for x in trans]
    metrics  = set(metrics)

    # prepare the contributions data structure which gets filled below
    contribs = {r: {
                m: [[0.0, 0.0]]
                   for m in metrics}
                for r in resrc}

    for entity in session.get():

        td    = entity.description
        etype = entity.etype

        transitions = tmap.get(etype)
        if not transitions:
          # print('no transitions for %s: etype %s' % (entity.uid, etype))
            continue

      # print('\n', entity.uid, etype, sorted(set([e[1] for e in entity.events])))
      # print()

        for trans in transitions:

            event  = trans[0]
            p_from = trans[1]
            p_to   = trans[2]

            try:
                t_resrc = {'cpu': entity.resources.get('cpu'),
                           'gpu': entity.resources.get('gpu')}

                # raptor tasks which were created in the master may not have
                # resources defined, or may not even have a task description
                # (they don't get an entry on MongoDB).  We thus guess their
                # resource consumption here.
                # NOTE: this can lead to underutilization to be reported!
                if not t_resrc['cpu'] and 'task' in entity.uid:
                    td = entity.description
                    if not td.get('cpu_processes'):
                        # guess
                        t_resrc = {'cpu': 1, 'gpu': 0}
                    else:
                        cores = td['cpu_processes'] * td['cpu_threads']
                        gpus  = td['cpu_processes'] * td['gpu_processes']
                        t_resrc = {'cpu': cores,
                                   'gpu': gpus}
              # print(entity.uid, p_from, p_to, t_resrc)

            except Exception as e:
                # if 'request' not in entity.uid:
                #     print('guess resources for %s' % entity.uid)

                # if 'pilot' in entity.uid:
                #     t_resrc = {'cpu': 1024 * 40,
                #                'gpu': 1024 *  8}
                # else:
                #     t_resrc = {'cpu': 1,
                #                'gpu': 0}
                raise RuntimeError(entity.uid + 'is missing resource '
                    'information. RA cannot know how many cores/GPUs were '
                    'requested. Session is likely corrupted. Aborting.') from e

            # we need to work around the fact that sub-agents have no separate
            # entity type, but belong to the pilot.  So instead we assign them
            # resources of 1 node.  We take those data from the pilot.
            if 'agent' in str(event):
                t_resrc = {'cpu': pilot.cfg['cores_per_node'],
                           'gpu': pilot.cfg['gpus_per_node' ]}

            ts = entity.timestamps(event=event)
            if not ts:
              # print('%s: no event %s for %s' % (uid, event, etype))
                continue

            for r in resrc:
                amount = t_resrc[r]
                if amount == 0:
                    continue
                t = (ts[0] - t_min)
                contribs[r][p_from].append([t, -amount])
                contribs[r][p_to  ].append([t, +amount])
              # print('%6.3f : %-30s : %-25s : %-15s --> %-15s [%s]' %
              #         (t, uid, event, p_from, p_to,   amount))

    # we now have, for all metrics, a list of resource changes, in the form of
    #
    #   [timestamp, change]
    #
    # where the change can be positive or negative.  From this, we now calculate
    # the continuous time series for the metrics: for each metric, sort the
    # contribution changes by time and calculate the running sum of the changes.

    series = dict()
    for r in contribs:

        series[r] = dict()
        for m in contribs[r]:

            series[r][m] = list()
            value = 0.0

            for c in sorted(contribs[r][m]):
                value += c[1]
                # normalize to pilot resources to obtain percent
                if p_resrc[r]:
                    if percent:
                        rel = value / p_resrc[r] * 100
                      # print('rel', rel)
                        series[r][m].append([c[0], rel])
                    else:
                        series[r][m].append([c[0], value])
                      # print('val %6.3f %-15s: %3d' % (c[0], m, value))
                else:
                    series[r][m].append([c[0], 0])

    x = {'min': x_min, 'max': x_max}

  # import pprint
  # pprint.pprint(p_resrc)
  # pprint.pprint(series)
  # pprint.pprint(x)

    return p_resrc, series, x


# ------------------------------------------------------------------------------
#
def get_pilots_zeros(ra_exp_obj):
    """Calculates when a set of pilots become available.

    Parameters
    ----------
    ra_exp_obj: ra.Experiment
                RADICAL-Analytics Experiment object with all the pilot entity
                objects for which to calculate the starting timestamp.

    Returns
    -------
    p_zeros: dict
             Session ID, pilot ID and starting timestamp. E.g.,
             {'re.session.login1.lei.018775.0005': {'pilot.0000':
             2347.582849740982}}.
    """

    p_zeros = {}
    for session in ra_exp_obj.sessions:
        p_zeros[session.uid] = {}
        for pilot in session.get(etype='pilot'):
            p_zeros[session.uid][pilot.uid] = pilot.timestamps(
                event={ru.EVENT: 'bootstrap_0_start'})[0]

    return p_zeros


# ------------------------------------------------------------------------------
#
def get_plot_utilization(metrics, consumed, t_zero, sid):
    """Calculates the resources utilized by a set of metrics. Utilization is
    calculated for each resource without stacking and aggregation. May take
    hours or days with >100K tasks, 100K resource items. Use get_pilot_series
    and stack_transitions instead.

    Parameters
    ----------
    metrics : list
              Each element is a list with name, metrics and color. E.g.,
              ['Bootstrap', ['boot', 'setup_1'], '#c6dbef'].
    consumed: dict
              min-max timestamp and resource id range for each metric and
              pilot. E.g., {'boot': {'pilot.0000': [[2347.582849740982,
              2365.6164498329163, 0, 167]}.
    t_zero  : float
              Start timestamp for the pilot.
    sid     : string
              Identifier of a ra.Session object.

    Returns
    -------
    legend : dict
             keys: Type of resource ('cpu', 'gpu'); values: list of
             matplotlib.lines.Line2D objects for the plot's legend.
    patches: dict
             keys: Type of resource ('cpu', 'gpu'); values: list of
             matplotlib.patches.Rectangle. Each rectangle represents the
             utilization for a set of resources.
    x      : dict
             Mix and max value of the X-axes.
    y      : dict
             Mix and max value of the Y-axes.
    """

    legend = list()

    x_min = None
    x_max = None
    y_min = None
    y_max = None

    patches = []

    for metric in metrics:

        color = metric[2]

        legend.append(mpl.lines.Line2D([0], [0], color=color, lw=6))

        if isinstance(metric, list):
            parts = metric[1]
        else:
            parts = [metric]

        for part in parts:
            for uid in consumed[sid][part]:
                for block in consumed[sid][part][uid]:
                    orig_x = block[0] - t_zero
                    orig_y = block[2] - 0.5
                    width  = block[1] - block[0]
                    height = block[3] - block[2] + 1.0

                    if x_min is None:
                        x_min = orig_x
                    if x_max is None:
                        x_max = orig_x + width
                    if y_min is None:
                        y_min = orig_x
                    if y_max is None:
                        y_max = orig_x + height

                    x_min = min(x_min, orig_x)
                    y_min = min(y_min, orig_y)
                    x_max = max(x_max, orig_x + width)
                    y_max = max(y_max, orig_y + height)

                    patch = mpl.patches.Rectangle((orig_x, orig_y),
                                                  width, height,
                                                  facecolor=color,
                                                  edgecolor='black',
                                                  fill=True, lw=0.0)

                    patches.append(patch)

    x = {'min': x_min, 'max': x_max}
    y = {'min': y_min, 'max': y_max}

    return legend, patches, x, y


# ------------------------------------------------------------------------------
#
def to_latex(data):
    '''
    Transforms the input string(s) so that it can be used as latex compiled plot
    label, title etc. Escapes special characters with a slash.

    Parameters
    ----------
    data : list or str
           An individual string or a list of strings to transform.

    Returns
    -------
    data : list of str
           Transformed data.
    '''

    if isinstance(data, list):
        return [to_latex(x) for x in data]

    if isinstance(data, str):
        return data.replace('%',  '\\%') \
                   .replace('#',  '\\#') \
                   .replace('_',  '\\_') \
                   .replace('$',  '\\$') \
                   .replace('&',  '\\&') \
                   .replace('~',  '\\~') \
                   .replace('^',  '\\^') \
                   .replace('{',  '\\{') \
                   .replace('}',  '\\}')

    return to_latex(str(data))


# ------------------------------------------------------------------------------
#
def tabulate_durations(durations):
    '''
    Takes a dict of durations as defined in rp.utils (e.g.,
    `rp.utils.PILOT_DURATIONS_DEBUG`) and returns a list of durations with their
    start and stop timestamps. That list can be directly converted to a
    panda.df.

    Parameters
    ----------
    durations : dict
                Dict of lists of dicts/lists of dicts. It contains
                details about states and events.

    Returns
    -------
    data : list
           List of dicts, each dict containing 'Duration Name',
           'Start Timestamp' and 'Stop Timestamp'.
    '''
    table = []
    for name in durations:
        duration = {}
        start = durations[name][0]
        stop  = durations[name][1]

        duration['Duration Name'] = name

        if list(start.values())[0] == 'state':
            duration['Start Timestamp'] = list(start.values())[1]
        else:
            duration['Start Timestamp'] = list(start.values())[0]

        if isinstance(stop, list):
            ds = []
            for state in stop:
                ds.append(list(state.values())[1])
            duration['Stop Timestamp'] = ', '.join(map(str, ds))
        else:
            if list(stop.values())[0] == 'state':
                duration['Stop Timestamp'] = list(stop.values())[1]
            else:
                duration['Stop Timestamp'] = list(stop.values())[0]

        table.append(duration)

    return table
