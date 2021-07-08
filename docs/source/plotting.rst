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
