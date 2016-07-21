Command-line utility to select a table within an HTML document and convert it
to CSV. Here we can get the historical population of Reykjavík from Wikipedia::

    $ htmltab h2+p+table.wikitable https://en.wikipedia.org/wiki/Reykjavík
    Year,City,Metro
    1801,600,
    1860,1450,
    1901,6321,8221
    1910,11449,14534
    1920,17450,21347
    1930,28052,33867
    1940,38308,43483
    1950,55980,44813
    1960,72407,88315
    1970,81693,106152
    1980,83766,121698
    1985,89868,
    1990,97569,145980
    1995,104258,
    2000,110852,175000
    2005,114800,187105
    2006,115420,191612
    2007,117721,196161
    2008,119848,201585
    2011,119108,202341
    2015,121822,

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

      If EXPRESSION is a number it will be used as an index to match the table
      in that position in the HTML document (e.g. '4' will match the fourth
      table in the document The first table has a position of 1, not 0.

      If not an integer, EXPRESSION can be a valid CSS selector or XPath
      expression. The selector or expression must match either a single 'table'
      element or one or more 'tr' elements.

    Options:
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
