``print``, ``format``, and ``%``, evolved.

    **Q:** It's been *forty years* since ``C`` introduced ``printf()`` and the basic
    formatted printing of positional parameters. Isn't it time for an upgrade?

    **A:** Yes! ZOMG, yes!
    
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

Printing Where You Like
=======================

``say()`` writes to a list of files--by default just ``sys.stdout``. But
with one simple configuration call, it will write to different--even
multiple--files::

    from say import say, stdout
    
    say.setfiles([stdout, "report.txt"])
    say(...)   # now prints to both stdout and report.txt

This has the advantage of allowing you to both capture and see
program output, without changing
any code (other than the config statement). You can also define your own targeted ``Say`` instances::

    from say import say, Say, stderr
    
    err = say.clone().setfiles([stderr, 'error.txt'])
    err("Failed with error {errcode}")  # writes to stderr, error.txt
    
Note that ``stdout`` and ``stderr`` are just convenience aliases to
the respective 
``sys`` equivalents.

Printing When You Like
======================

If you want to stop printing for a while::

    say.set(silent=True)  # no printing until set to False
    
Or transiently::

    say(...stuff..., silent=not verbose) # prints iff bool(verbose) is True

Of course, you don't have to print to any file. There's a predefined sayer
``fmt()`` that works exactly like ``say()`` and inherits most of
its options, but 
doesn't print. (The
``C`` analogy: ``say`` **:** ``fmt`` **::** ``printf`` **:** ``sprintf``.)

Indentation and Wrapping
========================

Indentation is a common way to display data hierarchically. ``say`` will
help you manage it. For example::

    say('TITLE')
    for item in items:
        say(item, indent=1)
   
will indent the items by one indentation level (by default, each indent
level is four spaces, but
you can change that with the ``indent_str`` option). 

If you want to change the default indentation level::

    say.set(indent=1)      # to an absolute level
    say.set(indent='+1')   # strings => set relative to current level
    
    ...
    
    say.set(indent=0)      # to get back to the default, no indent

Or you can use a ``with`` construct::

    with say.settings(indent='+1'):
        say(...)
        
        # anything say() emits here will be auto-indented +1 levels
        
    # anything say() emits here, after the with, will not be indented +1

And if you have a lot of data or text to print, you can easily wrap it::

    say("This is a really long...blah blah blah", wrap=40)
    
Will automatically wrap the text to the given width (using Python's standard ``textwrap`` module).

While it's easy enough for any ``print`` statement or function to have a few
space characters added to its format string, it's easy to mistakenly type too
many or too few spaces, or to forget to type them in some format strings. And if
you're indenting strings that themselves may contain multiple lines, the simple
``print`` approach breaks because won't take multi-line strings into account.
And it won't be integrated with wrapping.

``say``, however, simply handles the indent level and wrapping, and it properly
handles the multi-line string case. Subsequent lines will be just as nicely and
correctly indented as the first one--something not otherwise easily accomplished
without adding gunky, complexifying string manipulation code to every place in
your program that prints strings.

This starts to illustrate the "do the right thing" philosophy behind ``say``. So
many languages' printing and formatting functions a restricted to "outputting
values" at a low level. They may format basic data types, but they don't provide
straightforward ways to do neat text transformations like indentation that let
programmers rapidly provide correct, highly-formatted ouput. Over time, ``say``
will provide higher-level formatting options. For now: indentation and wrapping.

Encodings
=========

``say()`` and 
``fmt()`` try to work with Unicode strings, for example providing them as
return values. But character encodings remain a fractious and often exasperating
part of IT. When writing formatted strings, ``say`` handles this by encoding
into ``utf-8``.

If you are using strings containing ``utf-8`` rather than Unicode characters, ``say`` 
may complain. But it complains in the same places the built-in ``format()`` does,
so no harm done. (Python 3 doesn't generally allow ``utf-8`` in strings, so it's
cleaner on this front.)

You can get creative with the encoding::

    say('I am a truck!', encoding='base64')  # SSBhbSBhIHRydWNrIQo=

Or change the default::

    say.set(encoding='rot-13')
    
Knock yourself out with `all the exciting opportunites
<http://docs.python.org/library/codecs.html#standard-encodings>`_!
If you really want the formatted text returned just as it is written to files,
use the ``encoded`` option. Set to ``True`` and it returns text in the output
encoding. Or set to an actual encoding name, and that will be the return encoding.

``say()`` returns the formatted text with one small tweak: it removes the final
newline if a newline is the very last character. Though odd, this is exactly
what you need if you're going to ``print`` or
``say`` the resulting text without a gratuitous "extra" newline.

Titles and Horizontal Rules
===========================

``say`` defines a few convenience formatting functions::

    say.title('Errors', sep='-')
    for i,e in enumerate(errors, start=1):
        say("{i:3}: {e['name'].upper()}")
        
might yield::

    --------------- Errors ---------------
      1: I/O ERROR
      2: COMPUTE ERROR

A similar method ``hr`` produces just a horizontal line, like
the HTML ``<hr>`` element. For either, one can optionally 
specify the width (``width``), character repeated to make the line (``sep``),
and vertical separation/whitespace above and below the item (``vsep``).
Good options for the separator might be be '-', '=', or parts of the `Unicode 
box drawing character set <http://en.wikipedia.org/wiki/Box-drawing_character>`_.

Non-Functional Invocation
=========================

For those who don't want to always and forever surround "print statements" with
the Python 3-style function parentheses, the ``>`` operator is
provided as an experimental, non-functional way to print. The following
are identical::

    say> "{user.id}: {user.username}"
    say("{user.id}: {user.username}")
    
You can name as many values as you like in the format string, but there can
only be one format string, and no options. If you need to ``say`` multiple values,
or say them with statement-specific options, you must use the functional syntax.
    

Text and Templates
==================

Often the job of output is not about individual text lines, but about creating
multi-line files such as scripts and reports. This often leads away from standard
output mechanisms toward template pakcages, but ``say`` has you covered here as
well.::

    from say import Text
    
    # assume `hostname` and `filepath` already defined
    
    script = Text()
    script += """
        !#/bin/bash
        
        # Output the results of a ping command to the given file
        
        ping {hostname} >{filepath}
    """
    
    script.write_to("script.sh")
    
``Text`` objects are basically a list of text lines. In most cases, when you add
text (either as multi-line strings or lists of strings), ``Text`` will
automatically interopolate variables the same way ``say`` does. One can
simply ``print`` or
``say`` ``Text`` objects, as their ``str()`` value is the full text you would
assume. ``Text`` objects have both ``text`` and ``lines`` properties which
can be either accessed or assigned to.

``+=`` incremental assignment 
automatically removes blank starting and ending lines, and any whitespace prefix
that is common to all of the lines (i.e. it will *dedent* any given text).
This ensures you don't need to give up
nice Python program formatting just to include a template.

While ``+=`` is a handy way of incrementally building text, it
isn't strictly necessary in the simple example above; the
``Text(...)`` constructor itself accepts a string or set of lines.

Other in-place operators are: `|=`` for adding text while preserving leading white
space (no dedent) and ``&=`` adds text verbatim--without dedent or string
interpolation. 

One can ``read_from()`` a file (appending the contents of the file to the given
text object, with optional interpolation and dedenting). One can also 
``write_to()`` a file. Use the ``append`` flag if you wish to add to rather than
overwrite the file of a given name, and you can set an output encoding if you
like (``encoding='utf=8'`` is the default).

So far we've discussed``Text`` objects almost like strings, but they also act
as lists of individual lines (strings). They are, for example,
indexible via ``[]``, and they are iterable.
Their ``len()`` is the number of lines they contain. One can
``append()`` or ``extend()`` them with one or multiple strings, respectively.
``append()`` takes a keyword parameter ``interpolate`` that controls whether
``{}`` expressions in the string are interpolated. ``extend()`` additionally takes
a ``dedent`` flag that, if true, will
automatically remove blank starting and ending lines, and any whitespace prefix
that is common to all of the lines.

``Text`` objects, unlike strings, are mutable. The ``replace(x, y)`` method will
replace all instances of ``x`` with ``y`` *in situ*. If given just one argument,
a ``dict``, all the keys will be replaced with their corresponding values.

``Text`` doesn't have the full set of text-onboarding options seen in `textdata
<http://pypi.python.org/pypi/textdata>`_, but it should suit many cirumstances.
If you need more, ``textdata`` can be used alongside ``Text``.


Your Own Iterpolators
=====================

If you want to write your own functions that take strings and interpolate ``{}``
format tempaltes in them, you can look at ``say`` souce code and see how to
do it (see e.g. ``say.text.Text``). But there's an easier way::

    from say import caller_fmt
    
    def ucfmt(s):
        return caller_fmt(s).upper()

If ``ucfmt()`` had used ``fmt()``, it would not have worked. ``fmt()`` would
look for interpolating values within the context of ``ucfmt()`` and, not finding
any, probably raised an exception. But using ``caller_fmt()`` it looks into the
context of the caller of ``ucfmt()``, which is exactly where those values would
reside. *Voila!*

Python 3
========

Say works virtually the same way in Python 2 and Python 3. This can simplify 
software that should work across the versions, without all the ``from __future__
import print_function`` hassle.

``say`` attempts to mask some of the quirky compexities of the 2-to-3 divide,
such as string encodings and codec use.


Alternatives
============

 * `ScopeFormatter <http://pypi.python.org/pypi/ScopeFormatter>`_
   provides variable interpolation into strings. It is amazingly
   compact and elegant. Sadly, it only interpolates Python names, not full
   expressions. ``say`` has full expressions, as well as a framework for
   higher-level printing features beyond ``ScopeFormatter``'s...um...scope.

 * `interpolate <https://pypi.python.org/pypi/interpolate>`_ is 
   similar to ``say.fmt()``, in that it can 
   interpolate complex Python expressions, not just names.
   It's ``i % "format string"`` syntax is a little odd, however, in
   the way that it repurposes Python's earlier ``"C format string" % (values)``
   style ``%`` operator. It also depends on the native ``print`` statement
   or function, which doesn't help bridge Python 2 and 3.
   
 * Even simpler are invocations of ``%`` or ``format()``
   using ``locals()``. E.g.::
   
       name = "Joe"
       print "Hello, %(name)!" % locals()
       # or
       print "Hello, {name}!".format(**locals())
       
   Unfortunately this has even more limitations than ``ScopeFormatter``: it only supports
   local variables, not globals or expressions. And the interpolation code seems
   gratuitous. Simpler::
   
      say("Hello, {name}!")

Notes
=====

 *  The ``say`` name was inspired by Perl's `say <http://perldoc.perl.org/functions/say.html>`_,
    but the similarity stops there.
    
 *  The ``show`` debug printing functions previously in this package
    have been split into a separate package,
    `show <http://pypi.python.org/pypi/show>`_.
    
 *  A new text aggregation class, ``Text`` is now available.
   
 *  Automated multi-version testing is managed with the wonderful
    `pytest <http://pypi.python.org/pypi/pytest>`_
    and `tox <http://pypi.python.org/pypi/tox>`_. ``say`` is now
    successfully packaged for, and tested against, all late-model verions of
    Python: 2.6, 2.7, 3.2, and 3.3, as well as PyPy 1.9 (based on 2.7.2).
 
 *  ``say`` has greater ambitions than just simple template printing. It's part
    of a larger rethinking of how output should be formatted. ``show()`` and ``Text``
    are down-payments on this larger vision. Stay tuned for more.
 
 *  In addition to being a practical module in its own right, ``say`` is
    testbed for `options <http://pypi.python.org/pypi/options>`_, a package
    that provides high-flexibility option, configuration, and parameter
    management.
 
 *  The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
    `@jeunice on Twitter <http://twitter.com/jeunice>`_
    welcomes your comments and suggestions.
    
To-Dos
======

 *  Provide code that allows ``pylint`` to see that variables used inside
    the ``say`` and ``fmt`` format strings are indeed thereby used.

Installation
============

To install the latest version::

    pip install -U say

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade say
    
(You may need to prefix these with "sudo " to authorize installation.)
