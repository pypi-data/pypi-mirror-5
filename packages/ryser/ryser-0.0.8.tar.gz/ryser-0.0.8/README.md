Ryser - Latin Squares and Related Designs
=========================================

Created Wed Aug  8 15:39:10 BST 2012. Last updated Fri Sep 13 18:15:10 BST 2013.

Introduction
------------

Ryser is a Python package for latin squares and related designs.

Example: Hall Numbers
---------------------

Here is a demo which computes Hall numbers.

    >>> import ryser
    >>> from ryser.examples import eg3, fail4

    >>> S = fail4[0]
    >>> hall_nums = ryser.hall.symmetric_hall_numbers(eg3, S)

Test Hall inequalities:

    >>> assert ryser.hall.hall_inequality_on_cells(eg3, S)
    >>> assert not ryser.hall.symmetric_hall_inequality_on_cells(eg3, S)

Print the Hall numbers and show the subgraphs.

    >>> print "S: {}".format(S)
    >>> print "Hall numbers: {}".format(hall_nums)
    >>> print "Sum of Hall numbers: {}".format(sum(hall_nums))
    >>> print "No of vertices: {}".format((len(S))

    >>> ryser.hall.hall_subgraphs(eg3, S, format = 'dot')

