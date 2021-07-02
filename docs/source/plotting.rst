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

+------------+-----------------------------------------------------------------------+
| Hex        | Color                                                                 |
+============+=======================================================================+
| #1a80b2    |:raw-html:`<span style="background-color:#1a80b2">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #b2cce6    |:raw-html:`<span style="background-color:#b2cce6">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #ff801a    |:raw-html:`<span style="background-color:#ff801a">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #ffb280    |:raw-html:`<span style="background-color:#ffb280">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #339933    |:raw-html:`<span style="background-color:#339933">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #99e680    |:raw-html:`<span style="background-color:#99e680">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #cc3333    |:raw-html:`<span style="background-color:#cc3333">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #ff9999    |:raw-html:`<span style="background-color:#ff9999">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #9966b2    |:raw-html:`<span style="background-color:#9966b2">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #ccb2cc    |:raw-html:`<span style="background-color:#ccb2cc">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #804c4c    |:raw-html:`<span style="background-color:#804c4c">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #cc9999    |:raw-html:`<span style="background-color:#cc9999">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #e680cc    |:raw-html:`<span style="background-color:#e680cc">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #ffb2cc    |:raw-html:`<span style="background-color:#ffb2cc">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #b2b21a    |:raw-html:`<span style="background-color:#b2b21a">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #e6e699    |:raw-html:`<span style="background-color:#e6e699">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #1ab2cc    |:raw-html:`<span style="background-color:#1ab2cc">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #99e6e6    |:raw-html:`<span style="background-color:#99e6e6">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #4c4c4c    |:raw-html:`<span style="background-color:#4c4c4c">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #666666    |:raw-html:`<span style="background-color:#666666">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #808080    |:raw-html:`<span style="background-color:#808080">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #998080    |:raw-html:`<span style="background-color:#998080">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #99b2b2    |:raw-html:`<span style="background-color:#99b2b2">...............</td>`|
+------------+-----------------------------------------------------------------------+
| #cccccc    |:raw-html:`<span style="background-color:#cccccc">...............</td>`|
+------------+-----------------------------------------------------------------------+

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


