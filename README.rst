HTMLTab
=======

.. image:: https://travis-ci.org/flother/htmltab.svg
   :target: https://travis-ci.org/flother/htmltab
.. image:: https://codecov.io/gh/flother/htmltab/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/flother/htmltab

HTMLTab is a command-line utility to select a table within an HTML document and
convert it to CSV. Here we can get the historical population of Reykjavík from
Wikipedia::

    $ htmltab --select h2+p+table.wikitable https://en.wikipedia.org/wiki/Reykjavík
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

  Usage: htmltab [OPTIONS] [HTML_FILE]

    Select a table within an HTML document and convert it to CSV. By default
    stdin will be used as input, but you can also pass a filename or a URL.

    Unless otherwise specified, the first table element in the HTML document
    is converted to CSV. To change that behaviour pass an alternative using
    the '--select' option. The value may be an integer index, a CSS selector,
    or an XPath expression.

    To select the fourth table within the the file 'foo.html':

      htmltab --select 4 foo.html

    To select the table with the id 'data':

      htmltab --select table#data foo.html

    To select the rows within the second table inside the 'div' element with
    id 'bar', while excluding the rows in the header and footer:

      htmltab --select "(//div[@id='bar']//table)[2]/tbody/tr" foo.html

  Options:
    -s, --select TEXT               Integer index, CSS selector, or XPath
                                    expression that determines the table to
                                    convert to CSV.
    -n, --null-value TEXT           Case-sensitive value to convert to an empty
                                    cell in the CSV output. Use multiple times
                                    if you have more than one null value.
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
    --version                       Show the version and exit.
    --help                          Show this message and exit.


.. _Python 3: https://docs.python.org/3/
.. _Click: http://click.pocoo.org/6/
.. _lxml: http://lxml.de
.. _cssselect: https://pythonhosted.org/cssselect/
.. _Beautiful Soup 4: https://www.crummy.com/software/BeautifulSoup/
.. _requests: http://python-requests.org/
