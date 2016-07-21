Command-line utility to select a table within an HTML document and convert it
to CSV. Here we can get the historical population of Reykjavík from Wikipedia::

    $ htmltab -n '-' \
              -n '--' \
              --css h2+p+table.wikitable \
              https://en.wikipedia.org/wiki/Reykjavík | csvlook
    |-------+--------+---------|
    |  Year | City   | Metro   |
    |-------+--------+---------|
    |  1801 | 600    |         |
    |  1860 | 1450   |         |
    |  1901 | 6321   | 8221    |
    |  1910 | 11449  | 14534   |
    |  1920 | 17450  | 21347   |
    |  1930 | 28052  | 33867   |
    |  1940 | 38308  | 43483   |
    |  1950 | 55980  | 44813   |
    |  1960 | 72407  | 88315   |
    |  1970 | 81693  | 106152  |
    |  1980 | 83766  | 121698  |
    |  1985 | 89868  |         |
    |  1990 | 97569  | 145980  |
    |  1995 | 104258 |         |
    |  2000 | 110852 | 175000  |
    |  2005 | 114800 | 187105  |
    |  2006 | 115420 | 191612  |
    |  2007 | 117721 | 196161  |
    |  2008 | 119848 | 201585  |
    |  2011 | 119108 | 202341  |
    |  2015 | 121822 |         |
    |-------+--------+---------|

* Repository: https://github.com/flother/htmltab
* Issues: https://github.com/flother/htmltab/issues

Installation
------------

::

    pip3 install -e git+https://github.com/flother/htmltab#egg=htmltab

HTMLTab requires `Python 3`_, Click_, lxml_, cssselect_, `Beautiful Soup 4`_,
and requests_.

Usage
-----

.. code-block:: text

    Usage: htmltab [OPTIONS] [EXPRESSION] [HTML_FILE]

      Select a table within an HTML document and convert it to CSV. By default
      stdin will be used as input, but you can also pass a filename or a URL.

      EXPRESSION can be a number (using the '--index' option) that indexes a
      table in the HTML document, an XPath expression (using the '--xpath'
      option), or a CSS selector (using the '--css' option). By default '--
      index' is assumed, and the first table in the HTML document is used if no
      EXPRESSION is given.

      A table is defined as a single 'table' element, or a collection of one or
      more 'tr' elements. If a CSS selector or XPath expression matches anything
      else an error is returned.

    Options:
      -i, --index                     Interpret EXPRESSION as an index, starting
                                      from 1.
      -s, --css                       Interpret EXPRESSION as a CSS selector.
      -x, --xpath                     Interpret EXPRESSION as an XPath expression.
      -n, --null-value TEXT           Case-insensitive value to convert to an
                                      empty cell in the CSV output. Use multiple
                                      times if you have more than one null value.
                                      [default: 'na', 'n/a', '.', '-']
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
                                      [default: '$', '¥', '£', '€']
      --help                          Show this message and exit.


.. _Python 3: https://docs.python.org/3/
.. _Click: http://click.pocoo.org/6/
.. _lxml: http://lxml.de
.. _cssselect: https://pythonhosted.org/cssselect/
.. _Beautiful Soup 4: https://www.crummy.com/software/BeautifulSoup/
.. _requests: http://python-requests.org/
