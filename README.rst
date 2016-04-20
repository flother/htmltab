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

HTMLTab requires `Python 3`_, `Click`_, and `lxml`_.

Usage
-----

.. code-block:: text

    Usage: htmltab [OPTIONS] EXPRESSION HTML_FILE

      Select a table within an HTML document and convert it to CSV.

    Options:
      -c, --css              Use a CSS selector to determine the table (default).
      -x, --xpath            Use an XPath expression to determine the table.
      -i, --index            Use an index, starting from 1, to determine the
                             table.
      -n, --null-value TEXT  Case-insensitive value to convert to an empty cell in
                             the CSV output (defaults are 'na', 'n/a', '.', '-')
      --help                 Show this message and exit.


.. _Python 3: https://docs.python.org/3/
.. _Click: http://click.pocoo.org/6/
.. _lxml: http://lxml.de
