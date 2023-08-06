Simple, effective debug printing.

Logging, assertions, unit tests, and
interactive debuggers are all great development tools. But sometimes you
just need to print values as a program runs to see what's going on. Every
language has features to print text, but they're not really customized for
printing debugging information. ``show`` is. It provides a simple, DRY
mechanism to "show what's going on."

.. image:: https://pypip.in/d/show/badge.png
    :target: https://crate.io/packages/show/

Usage
=====

::

    from show import show

    x = 12
    nums = list(range(4))

    show(x, nums)

yields::

    x: 12  nums: [0, 1, 2, 3]

Debug Printing
==============

Sometimes programs print so that users can see things, and sometimes they print
so that develpopers can. ``show()`` is for developers, helping
rapidly print the current state of variables. It replaces require the craptastic
repetitiveness of::

    print "x: {0}".format(x)

with::

    show(x)

If you'd like to see where the data is being produced,::

    show.set(where=True)

will turn on location reporting. This can also be set on call-by-call basis.

For this and much more, see `the full documentation at Read the Docs
<http://show.readthedocs.org/en/latest/>`_. 

