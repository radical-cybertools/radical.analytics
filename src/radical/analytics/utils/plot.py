import os
import sys
import glob
import matplotlib as mpl
import radical.utils as ru
import radical.pilot as rp


# ------------------------------------------------------------------------------
#
def get_plotsize(width, fraction=1, subplots=(1, 1)):
    """ Set aesthetic figure dimensions to avoid scaling in latex.

    Parameters
    ----------
    width   : float
              Width in points (pts)
    fraction: float
              Fraction of the width which you wish the figure to occupy
    subplots: tuple
              Number of raws and number of columns of the plot

    Returns
    -------
    fig_dim : tuple
              Dimensions of figure in inches
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

    path  = os.path.dirname(sys.executable)
    path += '/../share/radical.analytics/styles'

    for path in glob.glob('%s/*.txt' % path):
        if path.endswith('/%s.txt' % name):
            return os.path.normpath(path)


# ------------------------------------------------------------------------------
#
def stack_transitions(series):
    '''create data frames for each metric and combine them into one data frame
    for alignment. Since transitions obviously happen at arbitrary times, the
    timestamps for metric A may see no transitions for metric B.  When using a
    combined timeline, we end up with NaN entries for some metrics on most
    timestamp, which in turn leads to gaps when plotting.  So we fill the NaN
    values with the previous valid value, which in our case holds until the next
    transition happens.
    '''

    dfs = [pd.DataFrame(series[r][m], columns=['time', m])
            for m in series[r]]

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

    # stacked plotting and area filling don't play well together in
    # matplotlib, so instead we use normal (unstacked) plot routines and
    # fill inbetween.  We thus manually compute the stacked numbers:
    # copy the timeline to a new data frame
    stacked = merged[['time']].copy()
    prev    = list()

    # for each metric, copy the metric column and add all previous colums
    for m in to_stack:
        stacked[m] = merged[m]
        for p in prev:
            stacked[m] += merged[p]
        prev.append(m)

    return stacked


# ------------------------------------------------------------------------------
#
def get_pilot_series(session, pilot, tmap, resrc):

    # get total pilot resources and runtime
    p_resrc = {'cpu': pilot.cfg['cores'],
               'gpu': pilot.cfg['gpus' ]}

    t_min = pilot.timestamps(event={1: 'bootstrap_0_start'})[0]
    t_max = pilot.timestamps(event={1: 'bootstrap_0_stop'})[0]


    t_span = t_max - t_min
    x_min  = 0
    x_max  = t_span + 0.05 * t_span

    # derive the pilot resource transition points from the metrics
    rpp = rp.utils.prof_utils

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

        if not trans:
            continue

        uid = entity.uid
        td  = entity.description

        # filter out worker ranks
        if uid.count('.') > 1:
            continue

        transitions = tmap.get(entity.etype, [])
        for trans in transitions:

            event  = trans[0]
            p_from = trans[1]
            p_to   = trans[2]

            try:
                t_resrc = {'cpu': entity.resources['cpu'],
                           'gpu': entity.resources['gpu']}

            except:
                if 'request' not in entity.uid:
                    print('guess resources for %s' % entity.uid)

                if 'pilot' in entity.uid:
                    t_resrc = {'cpu': 1024 * 40,
                               'gpu': 1024 *  8}
                else:
                    t_resrc = {'cpu': 1,
                               'gpu': 0}

            # we need to work around the fact that sub-agents have no separate
            # entity type, but belong to the pilot.  So instead we assign them
            # resources of 1 node.  We take those data from the pilot.
            if 'agent' in str(event):
                t_resrc = {'cpu': pilot.cfg['cores_per_node'],
                           'gpu': pilot.cfg['gpus_per_node' ]}

            ts = entity.timestamps(event=event)
            if not ts:
                continue

            for r in resrc:
                try:
                    amount = t_resrc[r]
                    if amount == 0:
                        continue
                    t = (ts[0] - t_min)
                    contribs[r][p_from].append([t, -amount])
                    contribs[r][p_to  ].append([t, +amount])
                except Exception as e:
                    pass


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
                    if use_percent:
                        rel = value / p_resrc[r] * 100
                        series[r][m].append([c[0], rel])
                    else:
                        series[r][m].append([c[0], value])
                else:
                    series[r][m].append([c[0], 0])

    return p_resrc, series, x_min, x_max


#
#
def get_pilots_zeros(ra_exp_obj):

    p_zeros = {}
    for session in ra_exp_obj.sessions:
        p_zeros[session.uid] = {}
        for pilot in session.get(etype='pilot'):
            p_zeros[session.uid][pilot.uid] = pilot.timestamps(
                event={ru.EVENT: 'bootstrap_0_start'})[0]

    return p_zeros



# ------------------------------------------------------------------------------
#
def get_plot_utilization(metrics, consumed, p_zeros, sid, pid):

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
                    orig_x = block[0] - p_zeros[sid][pid]
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

