In dealing with text, one quotes values all the time. Single quotes. Double
quotes. Curly quotes. Backticks. Funny Unicode quotes. HTML or XML markup code.
*Et cetera.*

For simple cases, this isn't hard, and there a lot of ways to do it::

    value = 'something'
    print '{x}'.replace('x', value)             # {something}
    print "'{}'".format(value)                  # 'value'
    print "'" + value + "'"                     # 'value'
    print "{}{}{}".format('"', value, '"')      # "value"
    print ''.join(['"', value, '"'])            # "value"

But for such a simple, common task as wrapping values in surrounding text, it
looks pretty ugly, it's very low-level, and it's easy to type the wrong
character here or there. The *ad hoc* nature makes quoting tiresome and
error-prone. It's never more so than when you're constructing multi-level quoted
strings, such as Unix command line arguments, SQL commands, or HTML attributes.

So this module provides an clean, consistent, higher-level alternative.

Usage
=====

::

    from quoter import single, double, backticks, braces

    print single('this')       # 'this'
    print double('that')       # "that"
    print backticks('ls -l')   # `ls -l`
    print braces('curlycue')   # {curlycue}

.. |laquo| unicode:: 0xAB .. left angle quote
    :rtrim:
.. |raquo| unicode:: 0xBB .. right angle quote
    :ltrim:
.. |lsquo| unicode:: 0x2018 .. left angle quote
    :rtrim:
.. |rsquo| unicode:: 0x2019 .. right angle quote
    :ltrim:
.. |ldquo| unicode:: 0x201C .. left angle quote
    :rtrim:
.. |rdquo| unicode:: 0x201D .. right angle quote
    :ltrim:

It pre-defines callable ``Quoters`` for a handful of the most common quoting styles:

 *  ``braces``  {example}
 *  ``brackets`` [example]
 *  ``angles`` <example>
 *  ``parens`` (example)
 *  ``double`` "example"
 *  ``single`` 'example'
 *  ``backticks`` \`example\`
 *  ``anglequote`` |laquo| example |raquo|
 *   ``curlysingle`` |lsquo| example |rsquo|
 *   ``curlysdouble`` |ldquo| example |rdquo|

But there are a *huge* number of ways you might want to wrap or quote text. Even
considering just "quotation marks," there are `well over a dozen
<http://en.wikipedia.org/wiki/Quotation_mark_glyphs>`_. There are also `numerous
bracketing symbols in common use <http://en.wikipedia.org/wiki/Bracket>`_.
That's to say nothing of the constructs seen in markup, programming, and
templating languages. So ``quoter`` couldn't possibly provide an option
for every possible quoting style. Instead, it provides a general-purpose
mechanism for defining your own::

    from quoter import Quoter

    bars = Quoter('|')
    print bars('x')                    # |x|

    plus = Quoter('+','')
    print plus('x')                    # +x

    para = Quoter('<p>', '</p>')
    print para('this is a paragraph')  # <p>this is a paragraph</p>

    variable = Quoter('${', '}')
    print variable('x')                # ${x}

Note that ``bars`` is specified with just one symbol. If only one is given,
the prefix and suffix are considered to be identical. If you really only want
a prefix or a suffix, and not both, then instantiate the ``Quoter`` with two, one
of which is an empty string, as in ``plus`` above. For symmetrical quotes, where
the length of the prefix and the suffix are the same, you can specify the prefix
and suffix all in one go. The prefix will be the first half, the second, the second half

In most cases, it's cleaner and more efficient to define a style, but
there's nothing preventing you from an on-the-fly usage::

    print Quoter('+[ ', ' ]+')('castle')   # +[ castle ]+

Formatting and Encoding
=======================

The Devil, as they say, is in the details. We often don't just want quote
marks wrapped around values. We also want those values set apart from
the rest of the text. ``quoter`` supports this with ``padding`` and ``margin``
settings patterned on the `CSS box model <http://www.w3.org/TR/CSS2/box.html>`_.
In CSS, moving out from content one finds padding, a border, and then a margin.
Padding can be thought of as an internal margin, and
the prefix and suffix strings like the border. With that in mind::

    print braces('this')                      # '{this}'
    print braces('this', padding=1)           # '{ this }'
    print braces('this', margin=1)            # ' {this} '
    print braces('this', padding=1, margin=1) # ' { this } '

If desired, the ``padding`` and ``margin`` can be given as
strings, though usually they will be integers specifying the
number of spaces surrounding the text.

One can also define the ``encoding`` used for each call, per instance, or
globally. If some of your quote symbols use Unicode characters, yet your output
medium doesn't support them directly, this is an easy fix. E.g.::

    Quoter.options.encoding = 'utf-8'
    print curlydouble('something something')

Now ``curlydouble`` will output UTF-8 bytes. But in general, you should work in
Unicode strings in Python, encoding or decoding only at the time of input and
output, not as each piece of content is constructed.

Shortcuts
=========

One often sees very long function calls and expressions as text parts are being
assembled. In order to reduce this problem, ``quoter`` defines aliases for
``single``, ``double``, and ``triple`` quoting, as well as ``backticks``::

    from quoter import qs, qd, qt, qb

    print qs('one'), qd('two'), qb('and'), qt('three')
    # 'one' "two" `and` """three"""

You can, of course, define your own aliases as well, and/or redefine existing
styles. If, for example, you like ``braces`` but wish it added a padding space
by default, it's simple to redefine::

    braces = Quoter('{', '}', padding=1, name='braces')
    print braces('braces plus spaces!')  # '{ braces plus spaces! }'

You could still get the no-padding variation with::

    print braces('no space braces', padding=0) # '{no space braces}'

Dynamic Quoters
===============

It is possible to define ``Quoters`` that don't just concatenate text, but
that examine it and provide dynamic rewriting on the fly. For example,
in finance, one often wants to present numbers with a special formatting::

    from quoter import LambdaQuoter

    f = lambda v: ('(', abs(v), ')') if v < 0 else ('', v, '')
    financial = LambdaQuoter(f)
    print financial(-3)            # (3)
    print financial(45)            # 45

    password = LambdaQuoter(lambda v: ('', 'x' * len(v), ''))
    print password('secret!')      # xxxxxxx

    wf = lambda v:  ('**', v, '**') if v < 0 else ('', v, '')
    warning = LambdaQuoter(wf)
    print warning(12)              # 12
    print warning(-99)             # **-99**

The trick is instantiating ``LambdaQuoter`` with a callable (e.g. ``lambda``
expression or function) that accepts one value and returns a tuple of three
values: the quote prefix, the value (possibly rewritten), and the suffix.

``LambdaQuoter`` is an edge case, arcing over towards being
a general formatting function. That has the virtue of
providing a consistent mechanism for tactical output transformation
with built-in margin and padding support. But, one could argue that
such full transformations are "a bridge too far" for a quoting module.
So use the dynamic component of``quoter``, or not, as you see fit.


Extended X/HTML Usage
=====================

There is an extended quoting mode designed for XML and
HTML construction.

Instead of prefix and suffix strings, they use tag names. Or
more accurately, tag specifications. Like `jQuery <http://jquery.com>`_
``XMLQuoter`` and ``HTMLQuoter`` support
``id`` and ``class`` attributes in a style similar to
that of CSS selectors. It also understands that some
elements are 'void', meaning they do not want or need
closing tags.::

    from quoter import HTMLQuoter

    para = HTMLQuoter('p')
    print para('this is great!', {'class':'emphatic'})
    print para('this is great!', '.emphatic')

    print para('First para!', '#first')

    para_e = HTMLQuoter('p.emphatic')
    print para_e('this is great!')
    print para_e('this is great?', '.question')

    br = HTMLQuoter('br', void=True)
    print br()

yields::

    <p class='emphatic'>this is great!</p>
    <p class='emphatic'>this is great!</p>
    <p id='first'>First para!</p>
    <p class='emphatic'>this is great!</p>
    <p class='question'>this is great?</p>
    <br>

``HTMLQuoter`` quotes attributes by default with single quotes. If you
prefer double quotes, you may set them when the element is defined::

    div = HTMLQuoter('div', attquote=double)

``HTMLQuoter`` basically works, but buyer beware: It's not as well tested as the
rest of the module.

``XMLQuoter`` adds one additional attribute:
``ns`` for namespaces. Thus::

    item = XMLQuoter(tag='item', ns='inv')
    print item('an item')

yields::

    <inv:item>an item</inv:item>

Alternate API
=============

As an organizational assist, various quoters are available as
named attributes of pre-defined ``quote``, ``xml`` and ``html``
objects. This will also assist in strict imports, such as
``from quoter import quote``, yet without much loss of generality.

For ``quote``, attribute-accessed styles are generally the normal
expected styles
such as ``quote.double()`` or ``quote.braces()`` as qualified access
points for ``double()`` and ``braces()`` respectively.

For XML and HTML,
individual quoters/styles are automagically generated upon
first use based on pre-defined ``xml`` and ``html`` items. For example,
``html.b('this')`` creates an ``HTMLQuoter(tag='b', name='b')``
quoter that is cached as ``html.b`` for subsequent uses. Want a ``<strong>``
tag instead? No problem. ``html.strong('this')``. There is no
restriction on the tags you can request, including tags that are not valid
HTML.
You can also access ``html.comment()`` and ``xml.comment()`` for commenting
purposes.

In the future, additional quoting styles such as ones for Markdown or RST format
styles might appear.

A final tweak, if you specify a ``style`` attribute and provide the name of
a style, that's the style you get. ``quote.double(style='single')`` gives
the effect of ``quote.single``.  If you don't want confusing double-bucky
forms, don't use them. ``qs(...)``, ``quote.single(...)`` or
``quote(..., style='single')`` are much simpler, anyway.

Notes
=====

 * ``quoter`` provides simple transformations that could be alternatively
   implemented as a series of small functions. The problem is that such "little
   functions" tend to be constantly re-implemented, in different ways, and
   spread through many programs. That need to constantly re-implement such
   common and straightforward text formatting has led me to re-think how
   software should format text. ``quoter`` is one facet of a project to
   systematize higher-level formatting operations. See `say <http://pypi.python.org/pypi/say>`_
   and `show <http://pypi.python.org/pypi/show>`_
   for the larger effort.

 * ``quoter`` is also a test case for `options <http://pypi.python.org/pypi/options>`_,
   a module that supports flexible option handling.

 * Automated multi-version testing is managed with the magnificent
   `pytest <http://pypi.python.org/pypi/pytest>`_
   and `tox <http://pypi.python.org/pypi/tox>`_. Now
   successfully packaged for, and tested against, Python 2.6, 2.7, 3.2, and 3.3,
   as well as PyPy 2.1 (based on 2.7.3).

 * The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
   `@jeunice on Twitter <http://twitter.com/jeunice>`_ welcomes your comments
   and suggestions.

Installation
============

::

    pip install -U quoter

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade quoter

(You may need to prefix these with "sudo " to authorize installation.)