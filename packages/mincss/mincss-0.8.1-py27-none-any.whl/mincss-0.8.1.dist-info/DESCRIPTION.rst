mincss
======

Clears the junk out of your CSS by finding out which selectors are
actually not used in your HTML.

By Peter Bengtsson, 2012-2013

Why?
----

With the onslaught of Twitter Bootstrap upon the world it's very
tempting to just download their whole fat 80+Kb CSS and serve it up
even though you're not using half of the HTML that it styles.

There's also the case of websites that have changed over time but
without the CSS getting the same amount of love refactoring. Then it's
very likely that you get CSS selectors that you're no longer or never
using.

This tool can help you get started reducing all those selectors that
you're not using.

Whitespace compression?
-----------------------

No, that's a separate concern. This tool works independent of
whitespace compression/optimization.

For example, if you have a build step or a runtime step that converts
all your CSS files into one (concatenation) and trims away all the
excess whitespace (compression) then the output CSS can still contain
selectors that are never actually used.

What about AJAX?
----------------

If you have a script that creates DOM elements in some sort of
``window.onload`` event then ``mincss`` will not be able to know this
because at the moment ``mincss`` is entirely static.

So what is a web developer to do? Simple, use ``/* no mincss */`` like
this for example:

    .logged-in-info {
        /* no mincss */
	color: pink;
    }

That tells ``mincss`` to ignore the whole block and all its selectors.



.. _changelog-chapter:

Changelog
=========

v0.8.1 (2013-04-05)
-------------------

The file ``download.js`` was missing from the tarball.

v0.8.0 (2013-02-26)
-------------------

Much faster! Unless you pass ``Processor(optimize_lookup=False)`` when
creating the processor instance. See
http://www.peterbe.com/plog/mincss-0.8

v0.7.0 (2013-02-13)
-------------------

Fixed bug with make absolute url of url like `http://peterbe.com` +
`./style.css`. Thanks @erfaan!

v0.6.1 (2013-02-12)
-------------------

The proxy app would turn `<script src="foo"></script>` into `<script
src="http://remote/foo"/>`. Same for iframe, textarea and divs.

v0.6.0 (2013-02-01)
-------------------

New option, `phantomjs` that allows you to download the HTML using
phantomjs instead of regular Python's urllib.


v0.5.0 (2013-01-24)
-------------------

New option `preserve_remote_urls` to `Processor()` class. Useful when
the hrefs in link tags are of different domain than the URL you're
processing.


v0.1 (2013-01-14)
-----------------

Initial release.

