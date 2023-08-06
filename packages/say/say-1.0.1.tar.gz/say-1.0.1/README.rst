``print``, ``format``, and ``%``, evolved.

    **Q:** It's been *forty years* since ``C`` introduced ``printf()`` and the basic
    formatted printing of positional parameters. Isn't it time for an upgrade?

    **A:** Yes! ZOMG, yes!

.. image:: https://pypip.in/d/say/badge.png
    :target: https://crate.io/packages/say/
    
``say`` supplements or replaces Python's ``print``
statement/function, ``format`` function/method, and ``%`` string interpolation
operator with higher-level facilities:

 *  Straightforward string formatting with DRY, Pythonic
    templates that piggyback the built in ``format()`` method,  
    formatting syntax, and well-proven underlying engine.
 *  A single output mechanism compatible with both Python 2.x and Python 3.x.
 *  Indentation and wrapping (to help stucture output)
 *  Convenience printing functions for horizontal rules (lines), titles, and
    vertical whitespace.
 *  Convenient template/text aggregator objects for easily building,
    reading, and writing mutli-line texts.
    
Usage
=====

::

    from say import say, fmt, show
    
    x = 12
    nums = list(range(4))
    
    say("There are {x} things.")
    say("Nums has {len(nums)} items: {nums}")
    
yields::

    There are 12 things.
    Nums has 4 items: [0, 1, 2, 3]

``say`` is basically a simpler, nicer recasting of::
    
    print "There are {} things.".format(x)
    print "Nums has {} items: {}".format(len(nums), nums)
    
(NB in Python 2.6 one must number each of the ``{}`` placeholders--e.g. ``"Nums
has {0} items: {1}"``-- in order to avoid a ``ValueError: zero length field name
in format`` error. Python 2.7 and later assume the placeholders are sequential.)
    
The more items that are being printed, and the complicated the ``format``
invocation, the more valuable having it stated in-line becomes. Note that full
expressions are are supported. They are evaluated in the context of the caller.

For this and much more, see `the full documentation at Read the Docs
<http://say.readthedocs.org/en/latest/>`_. 
