# HTMLTab

[![Results from latest push build](https://travis-ci.org/flother/htmltab.svg)](https://travis-ci.org/flother/htmltab)
[![Code coverage report](https://codecov.io/gh/flother/htmltab/branch/master/graph/badge.svg)](https://codecov.io/gh/flother/htmltab)

HTMLTab is a command-line utility to select a table within an HTML document and convert it to CSV. Here we can get the foreign-born population of Edinburgh from Wikipedia:

```sh
$ htmltab --select p+table.wikitable.plainrowheaders https://en.wikipedia.org/wiki/Edinburgh
Place of birth,Estimated resident population (2011)[117]
Poland,11651
India,4888
Ireland,4743
Mainland China [A],4188
United States,3700
Germany,3500
Pakistan,2472
Australia,2100
France,2000
Spain,2000
South Africa,1800
Canada,1800
Hong Kong,1600
```

* Repository: <https://github.com/flother/htmltab>
* Issues: <https://github.com/flother/htmltab/issues>

## Installation

HTMLTab is a Python package, and as such it needs [Python 3] to be installed on your system. Once Python's available you can install HTMLTab using Pip (preferably into a [virtual environment]):

```sh
pip install -e git+https://github.com/flother/htmltab#egg=htmltab
```

You can also install it system-wide using [Pipx]:

```sh
pipx install git+https://github.com/flother/htmltab#egg=htmltab
```

When installation is complete, you'll have a new `htmltab` command available in your favourite shell.

## Usage

```sh
$ htmltab --help
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

  The CSV data will be output to stdout unless the '--output' option is
  specified.

Options:
  -s, --select TEXT               Integer index, CSS selector, or XPath
                                  expression that determines the table to
                                  convert to CSV.

  -n, --null-value TEXT           Case-sensitive value to convert to an empty
                                  cell in the CSV output. Use multiple times
                                  if you have more than one null value.
                                  [default: 'NA', 'N/A', '.', '-']

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

  -o, --output FILENAME           Write output to file instead of stdout
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

[Python 3]: https://docs.python.org/3/
[virtual environment]: https://realpython.com/python-virtual-environments-a-primer/
[Pipx]: https://pipxproject.github.io/pipx/
