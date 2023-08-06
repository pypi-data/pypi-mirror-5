.. Created 18 December 2010. Last updated Wed Aug 22 11:32:06 BST 2012

========
Tutorial
========

Completing partial latin squares
================================

Consider the following partial latin square.

.. math::
    
    \begin{array}{|c|c|c|}
      \hline a & . & c \\
      \hline b & c & . \\
      \hline . & a & b \\ \hline
    \end{array}

To make use of Ryser components for completing partial latin squares, you first
need to know how to create partial latin squares. The components for building
partial latin square objects lie in the :py:mod:`designs` module. So, we need to 
make names from that module available in the current workspace::

    >>> from ryser.designs import Latin
     
To build a partial latin square object we use a dictionary mapping cell labels
to symbols. The mapping is completely general, you can use whatever labels you
like and whatever symbols you like::     
     
    >>> P = { (0,0): 'a', (0,2): 'c', (1,0): 'b', (1,1): 'c', (2,1): 'a', (2,2): 'b' }
           
With this data in place we can now build a partial latin square object::
    
    >>> Latin(P, 3)
     
Notice how the dimensions of the latin square are given as a parameter to the
constructor.      

Parallel Testing of Hall's Condition
====================================

In this section we demonstrate how to use components of Ryser to decide
whether Hall's condition is satisfied for a certain partial latin square.
We place a special emphasis on parallel testing and demonstrate some scripts
which are available in Ryser to make it easy to create parallel jobs for the
cloud (via PiCloud) or for high-performance clusters.

.. code-block:: bash

    $ time python counterexample_investigation.py 0 256 > output.txt

    real    0m9.357s
    user    0m9.070s
    sys     0m0.140s
    $ grep False output.txt
    $ wc -l output.txt
    256 output.txt
    $ head -n 1 output.txt
    [45, 46, 47, 48, 57, 58, 59, 60, 69, 70, 71, 72, 81, 82, 83, 84, 93, 94, 95, 96] True
    $ tail -n 1 output.txt
    [45, 46, 47, 48, 57, 58, 59, 60, 69, 70, 71, 72, 81, 82, 83, 84, 93, 94, 95, 96, 107, 108, 119, 120, 105, 118, 131, 144] True

Completing sudoku puzzles
=========================

In this section we discuss completing sudoku puzzles.

Enumerating shidoku puzzles
===========================

In this section we build a simple experiment script to enumerate shidoku.

Embedding latin rectangles
==========================

In this section we discuss embedding latin rectangles.

Constructing magic squares
==========================

In this section we discuss magic squares.

