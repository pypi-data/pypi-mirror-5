Markdown is great, but if you want pretty "curled" quotes, real em- and
en-dashes, and the other typographic prettification that our modern Unicode- and
Web-savvy world affords, it needs to be married with ``smartypants`` (or an
equivalent module) to turn ugly, programmer-ish punctuation into pretty
typographic punctuation. This module does that.

Usage
=====

::
  
    import markdown
    
    text = """
    Markdown makes HTML from simple text files. But--it lacks typographic
    "prettification." That... That'd be sweet. Definitely 7---8 on a '10-point
    scale'. Now it has it.
    
    Huzzah!
    """
    
    print markdown.markdown(text, extensions=['smartypants'])

This produces nice HTML output, including typographically "pretty" quotes and
other punctuation. It also renders HTML entities in their named rather than
numeric form, which is easier on the eyes and more readily comprehended::

    <p>Markdown makes HTML from simple text files. But&mdash;it lacks
    typographic &ldquo;prettification.&rdquo; That&hellip; That&rsquo;d be
    sweet. Definitely 7&ndash;8 on a &lsquo;10-point scale&rsquo;. Now it has
    it.</p>
    <p>Huzzah!</p>
    
Note that you don't really need to do an ``import mdx_smartypants``.
You're welcome to if you like, and it may help to advertise that the code
depends on ``mdx_smartypants`` being available. But ``markdown`` will
look for ``mdx_smartypants`` simply
by virtue of the ``extensions=['smartypants']`` declaration.

``mdx_smartypants`` will not massage indented code blocks, so your
program snippets are safe.

RTL Languages and Alternative Quotation Marks
=============================================

`Right-to-left languages <http://en.wikipedia.org/wiki/Right-to-left>`_ such as
Arabic, Hebrew, Persian, and Urdu reverse the convention seen in English and
other left-to-right languages. The "left" quotation mark is really the
"starting" quotation mark--and it should appear to the right of the "right"
quotation mark. The "right" quotation mark, similarly, is really the "ending"
mark, and appears to the left of the "right" mark. This is clearly not something
that was front-and-center even to the internationally-minded Unicode community,
given how "left" and "right" are embedded in the official glyph names--a
misnomer that carries over into HTML entities.

The historical ``smartypants`` module similarly thinks in LTR terms. It even
hard-codes the HTML entities used for quotation marks. To address this, this
module's bundled ``spants`` derivative uses variable quotation marks, and
provides a middleman class ``Quotes`` which allows defining which HTML entities
should be used for starting single, ending single, starting double, and ending
double quotation marks, respectively. It also provides a mechanism for defining
the directionality of text. When emitting for RTL languages, the normal
left/right conventions are reversed.

``Quotes.set(ssquo, esquo, sdquo, edquo, dir)`` allows you to set one or more of
these values. If you are changing the direction of quoting  away from LTR, it's
best to redefine all of the quotes so that everything is consistently defined and
ordered.

``Quotes.reset()`` puts everything back to factory defaults. Perhaps most
usefully, ``Quotes.configure_for_text(text)`` guesses what direction the
language is rendered, and sets quotes accordingly. In order to provide a
fire-and-forget experience, unless the user sets the language direction
explicitly, this heuristic will be invoked as a normal part of
``mdx_smartypants`` operation. Also note: If called directly, this API must be
provided pure, plain text--not text wrapped in HTML or other markup (which will
fool the language guesser into improperly guessing English). If the user has
explicitly set language direction, the guess will not be made--but an optional
``force`` Boolean parameter can be supplied to specify that previous explicit
direction setting should be ignored, and guessing commenced.

This API and functionality is brand new; tests have been added and successfully
passed for it, but it should be considered somewhat experimental for now.


.. |lsquo| unicode::  U+2018 .. left single quote
.. |rsquo| unicode::  U+2019 .. right single quote
.. |ldquo| unicode::  U+201C .. left double quote
.. |rdquo| unicode::  U+201D .. right double quote
.. |laquo| unicode::  U+00AB .. left angle quote  / guillemet
.. |raquo| unicode::  U+00BB .. right angle quote / guillemet
.. |lasquo| unicode:: U+2039 .. left single angle quote
.. |rasquo| unicode:: U+203A .. right single angle quote
.. |bdquo| unicode::  U+201E .. low double quote
.. |sbquo| unicode::  U+201A .. low single quote


Digging even deeper, `a great variety and vast diversity of different
quotation styles <https://en.wikipedia.org/wiki/Non-English_usage_of_quotation_marks>`_
are used in different languages. While there is no automatic support
for styles that differ from English, ``Quotes.set`` can be called
with any HTML entities,
allowing pretty much any convention to be supported. For example::

    Quotes.set('&laquo;', '&raquo;', '&lasquo;', '&rasquo;')  # Swiss French
    Quotes.set('&sbquo;', '&laquo;', '&bdquo;',  '&ldquo;')   # German or Czech
   
For |laquo| Swiss |raquo| and |lasquo| French |rasquo| (first one)
and |bdquo| German |ldquo| and |sbquo| Czech |lsquo| (second one).
    
**NB** I do not have any experience with RTL, top-to-bottom languages such as
traditional Chinese and Japanese scripts. If additional changes are required to
properly support that directionality, I'd be happy to hear about it.

Notes
=====

 *  As of version 1.4, ``mdx_smartpants`` attempts to automagically guess the
    direction of text flow used by the underlying language (e.g. LTR or RTL) and
    arrange quotation marks accordingly. Thanks to `Ahmad Khayyat
    <https://bitbucket.org/akhayyat>`_ for the bug report and discussion that
    led to this upgrade. This release also moved to a package-oriented distribution,
    given the additional modules required.
    
 *  As of version 1.2, ``mdx_smartpants`` no longer uses the stock
    ``smartypants`` module from PyPI. It incorporates a copy of the module,
    called ``spants``, in order to tweak the code for Python 3 compatibility, to
    fix the incorrect munging of punctuation within style blocks, and to make
    other improvements. This is a partial step towards a rewrite of
    ``smartypants`` itself to support Python 3 and be more in-line with modern
    Python idioms.
 
 *  Now successfully packaged for, and tested against, against Python 2.6, 2.7,
    and 3.3, as well as against PyPy 1.9 (based on 2.7.2). As of Version 1.4,
    official support for Python 2.5 and 3.2 withdrawn; while it may work on
    these, I can no longer test those versions. Also, they're obsolete. Time to
    upgrade!
   
 *  Automated multi-version testing managed by the awesome `pytest
    <http://pypi.python.org/pypi/pytest>`_ and `tox
    <http://pypi.python.org/pypi/tox>`_.

 *  The author, `Jonathan Eunice <mailto:jonathan.eunice@gmail.com>`_ or
    `@jeunice on Twitter <http://twitter.com/jeunice>`_ welcomes your comments
    and suggestions.
   
Installation
============

::

    pip install -U mdx_smartypants
    
To use ``pip`` to install under a specific Python version, look for a
program such as ``pip-3.3`` (e.g. ``which pip-3.3`` on Unix derived systems).
Failing this, you may be able to ``easy_install`` under a specific Python version
(3.3 in this example) via::

    python3.3 -m easy_install --upgrade mdx_smartypants
    
(You may need to prefix these with "sudo " to authorize installation.)
