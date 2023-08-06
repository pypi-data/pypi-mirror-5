``print``, ``format``, and ``%``, evolved.

    **Q:** It's been *forty years* since ``C`` introduced ``printf()`` and the basic
    formatted printing of positional parameters. Isn't it time for an upgrade?

    **A:** Yes! ZOMG, yes!

.. image:: https://pypip.in/d/say/badge.png
    :target: https://crate.io/packages/say/

``say`` supplements or replaces Python's ``print``
statement/function, ``format`` function/method, and ``%`` string interpolation
operator with simpler, higher-level facilities. For example::

    from say import say

    x, nums, name = 12, list(range(4)), 'Fred'

    say("There are {x} things.")
    say("Nums has {len(nums)} items: {nums}")
    say("Name: {name!r}")

yields::

    There are 12 things.
    Nums has 4 items: [0, 1, 2, 3]
    Name: 'Fred'

At this level, ``say`` is basically a simpler, nicer recasting of::

    from __future__ import print_function

    print("There are {0} things.".format(x))
    print("Nums has {0} items: {1}".format(len(nums), nums))
    print("Name: {0!r}".format(name))

(And yes, you really do need that ``import`` and the
numerical sequencing of ``{}`` format specs if you want code
that works correctly from Python 2.6 forward from
a single code base.)

The more items being printed, and the more complicated the ``format``
invocation, the more valuable this simple inline specification becomes.
As more formatting functions come online, the complexity gap widens. For
example::

    say("His name is {name:style='red+bold'}")

Or::

    say.style(stars=lambda x: fmt('*** ', style='red') + \
                              fmt(x,      style='black') + \
                              fmt(' ***', style='red'))

    say(message, style='stars')


Beyond DRY, Pythonic templates that piggyback the
Python's well-proven ``format()`` method, syntax, and underlying engine,
``say``'s virtues include:

  * A single output mechanism identical and compatible across Python 2 and
    Python 3.
  * A companion ``fmt()`` object for string formatting.
  * Higher-order line formatting such as line numbering,
    indentation, and wrapping built in.
  * Convenient methods for common formatting items such as
    titles,
    horizontal separators, and
    vertical whitespace.
  * Convenient access to style-driven formatting, ANSI colors, and other
    text transformations/post-processing.
  * Easy output to one or more files, with no additional code.
  * Super-duper template/text aggregator objects for easily building,
    reading, and writing multi-line texts.

Take it for a test drive today! See also `the full documentation
at Read the Docs <http://say.readthedocs.org/en/latest/>`_.
