.. _chapter_plotting:

Plotting
========

RADICAL-Analytics does not provide plotting primitives. Instead, it offers helper methods that can be used with 3rd party plotting libraries.

Matplotlib
----------

RADICAL-Analytics provides a style for Matplotlib. Loading it guarantees an uniform look&feel across plots. The style is located at ``styles/radical_mpl.txt``.

Loading RADICAL-Analytics Style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    import matplotlib.pyplot as plt
    import radical.analytics as ra

    plt.style.use(ra.get_mplstyle("radical_mpl")

Default Color Cycler of RADICAL-Analytics Style
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. role:: raw-html(raw)
   :format: html

01. :raw-html:`<span style="display:inline-block;width:100px;background-color:#1a80b2">#1a80b2</span>`
02. :raw-html:`<span style="display:inline-block;width:100px;background-color:#b2cce6">#b2cce6</span>`
03. :raw-html:`<span style="display:inline-block;width:100px;background-color:#ff801a">#ff801a</span>`
04. :raw-html:`<span style="display:inline-block;width:100px;background-color:#ffb280">#ffb280</span>`
05. :raw-html:`<span style="display:inline-block;width:100px;background-color:#339933">#339933</span>`
06. :raw-html:`<span style="display:inline-block;width:100px;background-color:#99e680">#99e680</span><br>`
07. :raw-html:`<span style="display:inline-block;width:100px;background-color:#cc3333">#cc3333</span>`
08. :raw-html:`<span style="display:inline-block;width:100px;background-color:#ff9999">#ff9999</span>`
09. :raw-html:`<span style="display:inline-block;width:100px;background-color:#9966b2">#9966b2</span>`
10. :raw-html:`<span style="display:inline-block;width:100px;background-color:#ccb2cc">#ccb2cc</span>`
11. :raw-html:`<span style="display:inline-block;width:100px;background-color:#804c4c">#804c4c</span>`
12. :raw-html:`<span style="display:inline-block;width:100px;background-color:#cc9999">#cc9999</span><br>`
13. :raw-html:`<span style="display:inline-block;width:100px;background-color:#e680cc">#e680cc</span>`
14. :raw-html:`<span style="display:inline-block;width:100px;background-color:#ffb2cc">#ffb2cc</span>`
15. :raw-html:`<span style="display:inline-block;width:100px;background-color:#b2b21a">#b2b21a</span>`
16. :raw-html:`<span style="display:inline-block;width:100px;background-color:#e6e699">#e6e699</span>`
17. :raw-html:`<span style="display:inline-block;width:100px;background-color:#1ab2cc">#1ab2cc</span>`
18. :raw-html:`<span style="display:inline-block;width:100px;background-color:#99e6e6">#99e6e6</span><br>`
19. :raw-html:`<span style="display:inline-block;width:100px;background-color:#4c4c4c">#4c4c4c</span>`
20. :raw-html:`<span style="display:inline-block;width:100px;background-color:#666666">#666666</span>`
21. :raw-html:`<span style="display:inline-block;width:100px;background-color:#808080">#808080</span>`
22. :raw-html:`<span style="display:inline-block;width:100px;background-color:#998080">#998080</span>`
23. :raw-html:`<span style="display:inline-block;width:100px;background-color:#99b2b2">#99b2b2</span>`
24. :raw-html:`<span style="display:inline-block;width:100px;background-color:#cccccc">#cccccc</span>`

Plotting for Latex Documents
----------------------------

In LaTeX documents, scaling images make the overall look&feel of a plot difficult to predict. Often, fonts are too small or too large, lines, bars, dots and axes too thin or too thick, and so on. Thus, plots should not be scaled in LaTeX---e.g., ``width=0.49\textwidth`` should not be used to scale a figure down of 50%---but, instead, plots should be created with the exact size of a column or a page. Column and page sizes depends on the ``.sty`` used for the LaTeX document and need to be inspected in order to know how to size a plot. Further, plots need to have their own style so that size, color, font face and overall features are consistent, readable and "pleasant" to look at.

Workflow with Matplotlib and Latex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following assume the use of Matplotlib to create a plot that needs to be added to a LaTeX document for publication.

#. Create a laTeX document using the following template:

   .. code-block:: latex

    \documentclass{<your_style_eg_IEEEtran>}

    \newcommand{\recordvalue}[1]{%
      \typeout{%
        === Value of \detokenize{#1}: \the#1%
      }%
    }

    \begin{document}
      % gives the width of the current document in pts
      \recordvalue{\textwidth}
      \recordvalue{\columnwidth}
    \end{document}


#. Compile your LaTeX document---e.g., pdlatex your_document---and note down the size of the text and of the column expressed in points (pts).  An example output is shown below (shortened):

   .. code-block:: shell

    $ pdflatex test.tex
    This is pdfTeX, [...]
    [...]
    === Value of \textwidth  : 252.0pt
    === Value of \columnwidth: 516.0pt
    (./test.aux) )
    No pages of output.
    Transcript written on test.log.

#. Use ``ra.set_size()`` to compute the exact size of your plot. For a plot with a single figure that span the width of a IEEtran LaTeX column:

   .. code-block:: python

    fig, ax = plt.subplots(figsize=ra.get_plotsize(252))

   for plot with 1 row and 3 subplots that spans the whole width of a IEEtran LaTeX page:

   .. code-block:: python

    fig, axarr = plt.subplots(1, 3, figsize=(ra.set_size(516)))


Plotting Resource Utilization
-----------------------------

RADICAL-Analytics offers helper functions to plot resource utilizations. Currently, RA recognizes two type of resources: cpus and gpus. Given a RADICAL-Pilot session, RA helper functions take one resource type as input and return utilization, patches and legends for that type of resource. If you need to plot the utilization for both types of resources, you will need to create two separate plots. If needed, plots can be stacked.

#. Define the metrics you want to use for resource utilization. RADICAL-Analytics will calculate the utilization for each metric:

   .. code-block::

    metrics = [
        ['Pilot Startup', ['boot', 'setup_1']                         , '#1a80b2'],
        ['Warmup',        ['warm' ]                                   , '#b2cce6'],
        ['Exec RP',       ['exec_rp', 'exec_sh', 'term_sh', 'term_rp'], '#ccb2cc'],
        ['Exec Cmd',      ['exec_cmd']                                , '#9966b2'],
        ['Draining',      ['drain']                                   , '#339933']
    ]

   One can use more or fewer metrics, depending on the information that the plot needs to convey. For example, using only 'Exec Cmd' will show the time for which each resource was utilized to execute a given task.

   Find the list of all available metrics in ``rp.utils.PILOT_DURATIONS``; ``rp.utils.TASK_DURATIONS_DEFAULT``; ``rp.utils.TASK_DURATIONS_APP``; ``rp.utils.TASK_DURATIONS_PRTE``; ``rp.utils.ASK_DURATIONS_PRTE_APP``.

#. Create an ``ra.Experiment`` object and derive the provided and consumed resources for each metric:

   .. code-block::

    # Type of resource we want to plot: cpu or gpu
    rtype='gpu'

    # List of sessions of an experiment
    sessions = ['../data/raw/incite2021/re.session.login1.lei.018775.0005']

    # Get the resource utilization of the experiment for each metics
    exp = ra.Experiment(sessions, stype='radical.pilot')
    provided, consumed, stats_abs, stats_rel, info = exp.utilization(
      metrics=metrics, rtype=rtype)

   ``stats_abs``, ``stats_rel``, ``info`` contain information that can be used to summarize resource utilization for each session of the experiment.

#. Plot the resource utilization with Matplotlib:

   .. code-block::

    # LaTeX document column size (see RA Plotting Chapter)
    csize = 252
    fig, ax = plt.subplots(figsize=(ra.get_plotsize(csize)))

    # Get the start time of each pilot
    p_zeros = ra.get_pilots_zeros(exp)

    # Plot legend, patched, X and Y axes objects (here we know we have only 1
    # pilot)
    legend, patches, x, y = ra.get_plot_utilization(metrics, consumed, p_zeros,
                                                    sinfo['sid'],
                                                    sinfo['pid'][0])

    # Place all the patches, one for each metric, on the axes
    for patch in patches:
      ax.add_patch(patch)

    # Title of the plot. Facultative, requires info about session (see RA Info
    # Chapter)
    ax.set_title('%s Tasks - %s Nodes' % (sinfo['ntask'], int(sinfo['nnodes'])))

    # Format axes
    ax.set_xlim([x['min'], x['max']])
    ax.set_ylim([y['min'], y['max']])
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.xaxis.set_major_locator(MaxNLocator(5))

    # Add legend
    fig.legend(legend, [m[0] for m in metrics],
               loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)

    # Add axes labels
    fig.text(-0.02, 0.5, '%ss' % rtype.upper(), va='center',
             rotation='vertical')
    fig.text(0.5, -0.02, 'Time (s)', ha='center')

    # Save a publication quality plot
    plt.savefig('figures/incite_2021_ru.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figures/incite_2021_ru.png', dpi=300, bbox_inches='tight')

#. With multiple sessions added to the variable ``sessions``, we can utilize subplots to create a single figure with multiple resource utilization plots:

   .. code-block::

    # sessions you want to plot
    splot = [os.path.basename(s) for s in sids_pruned]
    nsids = len(splot)

    # Create figure and 1 subplot for each session
    # Use LaTeX document page size (see RA Plotting Chapter)
    fwidth, fhight = ra.get_plotsize(516, subplots=(1, nsids))
    fig, axarr = plt.subplots(1, nsids, sharex='col', figsize=(fwidth, fhight))

    # Avoid overlapping between Y-axes ticks and sub-figures
    plt.subplots_adjust(wspace=0.45)

    # Generate the subplots with labels
    i = 0
    j = 'a'
    legend = None
    for sid in splot:

        # Use a single plot if we have a single session
        if nsids > 1:
            ax = axarr[i]
            ax.set_xlabel('(%s)' % j, labelpad=10)
        else:
            ax = axarr

        # Get the start time of each pilot
        p_zeros = ra.get_pilots_zeros(exp)

        # Plot legend, patched, X and Y axes objects (here we know we have only 1 pilot)
        legend, patches, x, y = ra.get_plot_utilization(metrics, consumed, p_zeros, sid, ss[sid]['p'].list('uid')[0])

        # Place all the patches, one for each metric, on the axes
        for patch in patches:
            ax.add_patch(patch)

        # Title of the plot. Facultative, requires info about session (see RA Info Chapter)
        ax.set_title('%s Tasks - %s Nodes' % (ss[sid]['ntask'], int(ss[sid]['nnodes'])))

        # Format axes
        ax.set_xlim([x['min'], x['max']])
        ax.set_ylim([y['min'], y['max']])
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.xaxis.set_major_locator(MaxNLocator(5))

        i = i+1
        j = chr(ord(j) + 1)

    # Add legend
    fig.legend(legend, [m[0] for m in metrics],
              loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=5)

    # Add axes labels
    fig.text( 0.05,  0.5, '%ss' % rtype.upper(), va='center', rotation='vertical')
    fig.text( 0.5 , -0.2, 'Time (s)', ha='center')

    # Save a publication quality plot
    plt.savefig('figures/incite_2021_ru.pdf', dpi=300, bbox_inches='tight')
    plt.savefig('figures/incite_2021_ru.png', dpi=300, bbox_inches='tight')

The code above produces the following plots:

.. image:: images/ru_v1.png
    :width: 600
    :alt: Single resource utilization plot

.. image:: images/ru_v1_multi.png
   :alt: Figure with multiple resource utilization plots
