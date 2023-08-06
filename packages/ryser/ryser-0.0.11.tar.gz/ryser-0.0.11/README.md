Ryser - Latin Squares and Related Designs
=========================================

Created Wed Aug  8 15:39:10 BST 2012. Last updated Mon Sep 30 13:59:23 BST 2013.

Introduction
------------

Ryser is a Python package for latin squares and related designs.

Example: Hall Numbers
---------------------

Here is a demo which computes Hall numbers.

    >>> import ryser
    >>> from ryser.examples import eg3, fail4
    >>> S = fail4[0]
    >>> hall_nums = ryser.hall.symmetric_numbers(eg3, S)
    >>> print "Hall numbers: {}".format(hall_nums)
    Hall numbers: [0, 1, 2, 2, 3, 3, 4, 4]
    >>> print "Sum of Hall numbers: {}".format(sum(hall_nums))
    Sum of Hall numbers: 19

Test Hall inequalities:

    >>> ryser.hall.inequality_on_cells(eg3, S)
    True
    >>> ryser.hall.symmetric_inequality_on_cells(eg3, S)
    False

