====================
header-detail-footer
====================

Overview
========

The header_detail_footer module provides a way to read input streams
(usually text files) that contain header rows, a number of data rows,
and footer rows. The number of header and footer rows must be
specified when parsing begins. There can be zero or more header rows,
and zero or more footer rows. The detail rows are all of the rows
between the header and footer. If a file consists of just headers and
footers, there will be zero detail rows.

The module API single function, parse(), and several exceptions.

Note that the contents of the input are never inspected: it's just an
iterator whose contents are returned.

Typical usage
=============

This code shows a simple usage of the `parse()` function::

    >>> from header_detail_footer import parse
    >>> header, details, footer = parse(['header', 'row 1', 'row 2', 'footer'])
    >>> header()
    'header'
    >>> list(details())
    ['row 1', 'row 2']
    >>> footer()
    'footer'

The parse() function
====================

The parse() function takes 1 required parameter, the input
iterator. There are two optional parameters, header_lines and
footer_lines. Both default to 1. They represent the number of header
and footer lines present in the input, respectively.

parse() returns 3 callables which return iterators: header, details,
and footer. The returned header iterable returns the input header;
details returns the detail lines; and footer the input footer.

For header and footer, they return a single line if header_lines or
footer_lines is 1, respectively. Otherwise, including the case of 0
lines, they return a list::

    >>> header, details, footer = parse(['row 1', 'row 2', 'footer 1', 'footer 2'],
    ...                                 header_lines=0, footer_lines=2)
    >>> list(header())
    []
    >>> list(details())
    ['row 1', 'row 2']
    >>> list(footer())
    ['footer 1', 'footer 2']

The returned header iterator need never be called. If footer is ever
called, details must have been called and been exhausted, otherwise a
ValueError is raised::

    >>> header, detail, footer = parse(iter('abc'))
    >>> footer()
    Traceback (most recent call last):
        ...
    ValueError: called footer() before details() were exhausted

Exceptions
==========

HeaderError
-----------

Raised by `parser()` if the input does not contain enough lines for the header::

    >>> header, details, footer = parse(['row 1'], header_lines=3)
    Traceback (most recent call last):
        ...
    HeaderError: too few lines for header

FooterError
-----------

Raised by `parser()` if the input does contain enough lines for the
header, but not enough lines for the footer::

    >>> header, details, footer = parse(['row 1', 'row 2', 'row 3'],
    ...                                 header_lines=2, footer_lines=2)
    Traceback (most recent call last):
        ...
    FooterError: too few lines for footer
