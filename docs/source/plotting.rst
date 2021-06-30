Plotting
========

RADICAL-Analytics does not provide plotting primitives. Instead, it offers helper methods that can be used with 3rd party plotting libraries.

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


#. Use the RADICAL style for Matplotlib:

   .. code-block:: python

    import matplotlib.pyplot as plt
    import radical.analytics as ra

    plt.style.use(ra.get_style("radical_mpl")


#. Use ``ra.set_size()`` to compute the exact size of your plot. For a plot with a single figure that span the width of a IEEtran LaTeX column:

   .. code-block:: python

    fig, ax = plt.subplots(figsize=ra.set_size(252))

   for plot with 1 row and 3 subplots that spans the whole width of a IEEtran LaTeX page:

   .. code-block:: python

    fig, axarr = plt.subplots(1, 3, figsize=(ra.set_size(516)))

