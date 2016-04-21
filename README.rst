Command-line utility to select a table within an HTML document and convert it
to CSV. Here we can get the historical population of Reykjavík from Wikipedia::

    $ curl -s https://en.wikipedia.org/wiki/Reykjav%C3%ADk | \
    > htmltab -n '-' -n '--' h2+p+table.wikitable - | \
    > csvlook
    |-------+---------+----------|
    |  Year | City    | Metro    |
    |-------+---------+----------|
    |  1801 | 600     |          |
    |  1860 | 1,450   |          |
    |  1901 | 6,321   | 8,221    |
    |  1910 | 11,449  | 14,534   |
    |  1920 | 17,450  | 21,347   |
    |  1930 | 28,052  | 33,867   |
    |  1940 | 38,308  | 43,483   |
    |  1950 | 55,980  | 44,813   |
    |  1960 | 72,407  | 88,315   |
    |  1970 | 81,693  | 106,152  |
    |  1980 | 83,766  | 121,698  |
    |  1985 | 89,868  |          |
    |  1990 | 97,569  | 145,980  |
    |  1995 | 104,258 |          |
    |  2000 | 110,852 | 175,000  |
    |  2005 | 114,800 | 187,105  |
    |  2006 | 115,420 | 191,612  |
    |  2007 | 117,721 | 196,161  |
    |  2008 | 119,848 | 201,585  |
    |  2011 | 119,108 | 202,341  |
    |  2015 | 121,822 |          |
    |-------+---------+----------|

* Repository: https://github.com/flother/htmltab
* Issues: https://github.com/flother/htmltab/issues

Installation
------------

::

    pip3 install -e git+https://github.com/flother/htmltab#egg=htmltab

HTMLTab requires `Python 3`_, `Click`_, `lxml`_, and `Beautiful Soup 4`_.

Usage
-----

.. code-block:: text

    Usage: htmltab [OPTIONS] EXPRESSION HTML_FILE

      Select a table within an HTML document and convert it to CSV.

    Options:
      -s, --css                       Interpret EXPRESSION as a CSS selector
                                      (default).
      -x, --xpath                     Interpret EXPRESSION as an XPath expression.
      -i, --index                     Interpret EXPRESSION as an index, starting
                                      from 1.
      -n, --null-value TEXT           Case-insensitive value to convert to an
                                      empty cell in the CSV output. Use multiple
                                      times if you have more than one null value.
                                      [default: 'na', 'n/a', '.', '-')
      -c, --convert-numbers / -k, --keep-numbers
                                      Convert number-like strings into numbers
                                      (e.g. remove group symbols, percent signs)
                                      or leave unchanged.  [default: convert]
      -g, --group-symbol TEXT         Symbol used to group digits in numbers (e.g.
                                      the ',' in '1,000.00').  [default: ,]
      -d, --decimal-symbol TEXT       Symbol used to separate integer from
                                      fraction in numbers (e.g. the '.' in
                                      '1,000.00').  [default: .]
      -u, --currency-symbol TEXT      Currency symbol to remove when converting
                                      number-like strings. Use multiple times if
                                      you have more than one currency symbol
                                      [default: '$', '¥', '£', '€')
      --help                          Show this message and exit.


.. _Python 3: https://docs.python.org/3/
.. _Click: http://click.pocoo.org/6/
.. _lxml: http://lxml.de
.. _Beautiful Soup 4: https://www.crummy.com/software/BeautifulSoup/
