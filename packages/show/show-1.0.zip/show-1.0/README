Simple, effective debug printing.

Logging, assertions, unit tests, and
interactive debuggers are all great development tools. But sometimes you
just need to print values as a program runs to see what's going on. Every
language has features to print text, but they're not really customized for
printing debugging information. ``show`` is. It provides a simple, DRY
mechanism to "show what's going on."

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
``show`` is built atop the `options <http://pypi.python.org/pypi/options>`_ module
for configuration management, and also the output management of
`say <http://pypi.python.org/pypi/say>`_. All ``say`` options work in show. If you
``show()`` a literal string, it will be iterpolated as it would be in ``say``::

    show("{n} iterations, still running")

yields something like::

    14312 iterations, still running

But note::

    s = '{n} iterations'
    show(s)

yields::

    s: '{n} iterations'

See ``say`` `say <http://pypi.python.org/pypi/say>`_ for additional detail on its
operation. ``show`` directly supports many ``say`` methods such as
``blank_lines``, ``hr``, and ``title`` which are meant to simplify
and up-level common formatting tasks.

Turning Show On and Off
=======================

Often it's convenient to only display debugging information under some conditions,
such as when a ``debug`` flag is set. That often leads to multi-line conditionals
such as::

    if debug:
        print "x:", x, "y:", y, "z:", z

With ``show`` it's a bit easier. There's a keyword argument, also called
``show``, that controls whether anything is shown. Set it to ``True`` or ``False``
to show or not show, or set it to the debug flag::

    show(x, y, z, show=debug)

Or set the show/don't show more globally:

    show.set(show=False)  # turn off showing

You can also make multiple ``show`` instances that can be separately controlled::

    show_verbose = show.clone()
    show_verbose.set(show=verbose_flag)
    show_verbose(x, y, z)

Showing Collections
===================

The goal of ``show`` is to provide the most useful information possible,
in the quickest and simplest way. Not requiring programmers to explicitly
restate values and names in print statements is the start, but the module also
provides some additional functions that provide a bit more semantic value.
For example, ``say.items()`` is designed to make printing collections easy.
It shows not just the values, but also the cardinality (i.e., length) of the
collection::

    nums = list(range(4))
    show.items(nums)

yields::

    nums (4 items): [0, 1, 2, 3]

Showing Object Properties
=========================

::

    show.props(x)

shows the properties of object ``x``. ("Properties" here
is generic language for "values" or "attributes" associated with
an object, and isn't used in the technical sense of Python properties.)
Properties will be listed alphabetically, but with those starting with underscores
(``_``), usually indicating "private" data, sorted after those that are
conventionally considered public.

If ``x`` has real ``@property`` members, those too displayed. However, other class
attributes that ``x`` rightfully inherits, but that are not directly present in the
``x`` instance, will not be displayed.

An optional second
parameter can determine which properties are shown. E.g.::

    show.props(x, 'name,age')

Or if you prefer the keyword syntax, this is equivalent to::

    show(x, props='name,age')

Or if you'd like all properties except a few::

    show.props(x, omit='description blurb')

Showing Function Inputs and Outputs
===================================

::

    @show.inout
    def foo(a,b):
        return a + b

Will now show all invocations of `foo()` with both values passed in
and the result value returned.

Changing How Things Are Shown
=============================

By default, ``show`` uses Python's ``repr()`` function to format
values. You may prefer some other kind of representation or formatting,
however. For example, the ``pprint`` module pretty-prints data structures.
You can set it to be the default formatter::

    from pprint import pformat
    show.set(fmtfunc=pformat)

    # NB pformat, not pprint!

Or to configure ``pformat`` more precisely::

    show.set(fmtfunc=lambda x: pformat(x, indent=4, width=120, depth=5))

Or you can set more complex pretty printing functions, using syntax
highlighting and other transformations. As a convenience, ``show``
provides a method that uses ``pygments`` and
``pprint`` in concert to more attractively display text. Just::

    show.prettyprint()

does the trick. It also takes ``indent``, ``depth``, and ``width`` options
for ``pformat`` and the ``style`` (style name) option for ``pygments``.
Some style names to try::

    # monokai manni rrt perldoc borland colorful default
    # murphy vs trac tango fruity autumn bw emacs vim pastie
    # friendly native

Showing What's Changed
======================

::

    show.changed()

will display the value of local variables. When invoked again, only those
variables that have changed (since the last ``show.changed()`` in the same context)
will be displayed.

You may ``omit`` some local variables if you like.
By default, those starting with underscores (``_``) will be omitted, as
will those containing functions, methods, builtins, and other parts Python
program infrastructure. If you'd like to add those, or global variables into
the mix, that's easily done::

    show.changed(_private, MY_GLOBAL_VAR)

Will start watching those.

**NB** ``changed()`` used to be called ``watch()``. The old ``watch()`` method
will still work (it's just an alias to ``changed``), but in the future it will
be going away.

Showing What's There
====================

It's often helpful to figure out "what am I dealing with here? what attributes or
methods or properties are available to me?" This is where ``show.dir`` comes into
play. You could do ``show(dir(x))``, but ``show.dir(x)`` will show you more information,
and do so more compactly. It also allows you to filter out the often huge
hubbub of some objects. By default, it doesn't show any attributes starting with
double underscore
``__``. You can control what's omitted with the ``omit`` keyword argument.
``show.dir(x, omit=None)`` shows everything,
while ``show.dir(x, omit='_* proxy*')`` omits all the methods starting with an
underscore or the word "proxy."

Interactive Limitations
=======================

``show`` has  draft support for both interactive Python and iPython.
It works well at the
interactive prompt, and within imported modules. It cannot, however, be used
within functions and classes defined within the interactive session. This is
due to how Python supprots--or fails to support--introspection in this instance.
Whether this is a hard limit, or something
that can be worked around over time, remains to be seen.

See e.g. `this <http://stackoverflow.com/questions/13204161/how-to-access-the-calling-source-line-from-interactive-shell>`_.

Python under Windows does not support readline the same way it is supported
on Unix, Linux, and Mac OS X. As of version 0.60, experimental
support is provided for the use of ``pyreadline`` under Windows to correct
this variance. This feature is yet untested. Works/doesn't work reports welcome!

Notes
=====

 *  ``show`` is in its early days. Over time, it will provide additional
    context-specific output helpers. For example, the "diff" views of ``py.test``
    seem a high-value enhancement.

 *  ``show`` depends on introspection, with its various complexities. It assumes
    that all objects are new-style classes, and that your program has not
    excessively fiddled with class data (e.g. no screwing with ``__class``).
    Diverge from these assumptions, and all bets are off.

 *  Automated multi-version testing managed with the wonderful
    `pytest <http://pypi.python.org/pypi/pytest>`_
    and `tox <http://pypi.python.org/pypi/tox>`_. ``show`` is
    successfully packaged for, and tested against, most late-model verions of
    Python: 2.6, 2.7, and 3.3, as well as PyPy 2.0.2 (based on 2.7.3).

 *  The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
    `@jeunice on Twitter <http://twitter.com/jeunice>`_
    welcomes your comments and suggestions.

Installation
============

To install the latest version::

    pip install -U show

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade show

(You may need to prefix these with "sudo " to authorize installation.)
