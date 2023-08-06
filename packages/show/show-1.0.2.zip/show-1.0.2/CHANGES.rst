1.0.2 (September 2013)
''''''''''''''''''''''

  * Improved pretty printing of code snippets for ``@show.inout``
    and ``@show.retval`` decorators.
  * Made ``show`` also accept lamdbas to link to variable values.
  * Added ``noshow`` object for easy turning off of showing.
  * General cleanups. Tightened imports. Tweaked docs. Switched to
    ``FmtException`` from ``say>=1.0.4``, and separated extensions
    into won module.
  * Drove version information into ``version.py``

1.0.1 (September 2013)
''''''''''''''''''''''

  * Moved main documentation to Sphinx format in ./docs, and hosted
    the long-form documentation on readthedocs.org. README.rst now
    an abridged version/teaser for the module.

1.0 (September 2013)
''''''''''''''''''''

  * Improved robustness for interactive use. If names cannot be
    detected, still gives value result with ``?`` pseudo-name.
  * Improved typenames for ``show.dir`` and ``show.props``
  * Improved ``show.inout`` with full call string on function
    return. A bit verbose in small tests, but too easy to lose
    "what was this called with??" context in real-scale usage
    unless there is clear indication of how the function was
    called.
  * Improved omission of probably useless display properties
    via ``omit`` keyword.
  * Began to add support for showing properties even when proxied through
    another object. Currently limited to selected SQLAlchemy and
    Flask proxies. More
    to come.
  * Cleaned up source for better (though still quite imperfect),
    PEP8 conformance
  * Bumped version number to 1.0 as part of move to `semantic
    versioning <http://semver.org>`_, or at least enough of it so
    as to not screw up Python installation procedures (which don't
    seem to understand 0.401 is a lesser version that 0.5, because
    401 > 5).
  * Probably several other things I've now forgotten.
