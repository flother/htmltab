"""
Command-line utility to parse an HTML document, find a particular
``table`` element within the document, convert the table to CSV, and
output the CSV to ``stdout``.
"""
import csv
from decimal import Decimal, InvalidOperation
import sys

from bs4 import UnicodeDammit
import click
from lxml.etree import LxmlError
import lxml.html
from lxml.cssselect import SelectorError


DEFAULT_NULL_VALUES = ("na", "n/a", ".", "-")
DEFAULT_CURRENCY_SYMBOLS = ("$", "¥", "£", "€")


def numberise(value, group_symbol, decimal_symbol, currency_symbols):
    """
    Convert a string to a :class:`decimal.Decimal` object, if the string
    is number-like.

    A string's considered number-like if it's made up of numbers with
    or without group and decimal symbols, and optionally suffixed by
    percent signs, prefixed by a +/- sign, or surrounded by currency
    symbols. It's pretty lenient, and could easily parse something as a
    number when it's not, but it's good enough.

    Args:
        value: String to attempt to convert to a number
        group_symbol: symbol used to group digits in numbers (e.g. the
            ',' in '1,000.00')
        decimal_symbol: Symbol used to separate integer from fraction in
            numbers (e.g. the '.' in '1,000.00').
        currency_symbols: List of currency symbols.

    Returns:
        :class:`decimal.Decimal`

    Raises:
        :class:`ValueError`: ``value`` is not numeric
    """
    number = value.strip("%")
    if len(number) > 0 and number[0] == "-":
        number = number[1:]
        sign = Decimal("-1")
    else:
        sign = Decimal("1")
    for symbol in currency_symbols:
        number = number.strip(symbol)
    number = number.replace(group_symbol, "")
    number = number.replace(decimal_symbol, ".")
    try:
        return Decimal(number) * sign
    except InvalidOperation:
        raise ValueError("{} is not numeric".format(value))


@click.command()
@click.option("--css", "-e", "language", flag_value="css", default=True,
              help="Interpret EXPRESSION as a CSS selector (default).")
@click.option("--xpath", "-x", "language", flag_value="xpath",
              help="Interpret EXPRESSION as an XPath expression.")
@click.option("--index", "-i", "language", flag_value="index",
              help="Interpret EXPRESSION as an index, starting from 1.")
@click.option("--null-value", "-n", multiple=True,
              help="Case-insensitive value to convert to an empty cell in the "
                   "CSV output. Use multiple times if you have more than one "
                   "null value.  [default: '{}']".format("', '".join(
                       DEFAULT_NULL_VALUES)))
@click.option("--convert-numbers/--keep-numbers", "-c/-k", is_flag=True,
              default=True, help="Convert number-like strings into numbers "
                                 "(e.g. remove group symbols, percent signs) "
                                 "or leave unchanged.  [default: convert]")
@click.option("--group-symbol", "-g", default=",", show_default=True,
              help="Symbol used to group digits in numbers (e.g. the ',' in "
                   "'1,000.00').")
@click.option("--decimal-symbol", "-d", default=".", show_default=True,
              help="Symbol used to separate integer from fraction in numbers "
                   "(e.g. the '.' in '1,000.00').")
@click.option("--currency-symbol", "-s", multiple=True,
              help="Currency symbol to remove when converting number-like "
                   "strings. Use multiple times if you have more than one "
                   "currency symbol  [default: '{}']".format("', '".join(
                       DEFAULT_CURRENCY_SYMBOLS)))
@click.option("--url", "-u", help="Fetch HTML document from url"
              "from url.")
@click.option("--file", "-f", type=click.File("rb"), help="Read HTML document "
              "from file or stdin")
@click.argument("expression")
def main(language, null_value, convert_numbers, group_symbol, decimal_symbol,
         currency_symbol, expression, url, file):
    """
    Select a table within an HTML document and convert it to CSV.
    """
    # Ensure ``SIGPIPE`` doesn't throw an exception. This prevents the
    # ``[Errno 32] Broken pipe`` error you see when, e.g., piping to ``head``.
    # For details see http://bugs.python.org/issue1652.
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (ImportError, AttributeError):
        # Do nothing on platforms without signals or ``SIGPIPE``.
        pass
    html_file = None
    if url is not None:
        import requests
        from io import StringIO
        r = requests.get(url)
        html_file = StringIO(r.text)
    elif file is not None:
        html_file = file
    if not html_file:
        raise click.UsageError("No HTML document supplied. Use either the "
                               "-u or -f option")
    # Read the HTML file using lxml's HTML parser, but convert to Unicode using
    # Beautiful Soup's UnicodeDammit class.
    try:
        unicode_html = UnicodeDammit(html_file.read(), smart_quotes_to="html",
                                     is_html=True)
        if unicode_html.unicode_markup is None:
            raise click.UsageError("no HTML provided.")
        if not unicode_html.unicode_markup:
            raise click.UsageError("could not detect character encoding.")
        doc = lxml.html.fromstring(unicode_html.unicode_markup)
    except (LxmlError, TypeError):
        raise click.UsageError("could not parse HTML.")

    # Find the element(s) that match the CSS selector, XPath expression, or
    # index.
    try:
        if language == "css":
            table = doc.cssselect(expression)
        elif language == "xpath":
            table = doc.xpath(expression)
        elif language == "index":
            table = doc.xpath("(//table)[{}]".format(int(expression)))
    except (SelectorError, lxml.etree.LxmlError, ValueError):
        # Either the CSS selector was invalid, the XPath expression was
        # invalid, or the index wasn't an integer.
        raise click.BadParameter(expression)

    # Complain if more than one element was returned.
    if len(table) != 1:
        raise click.UsageError("expression matched {} elements.".format(
            len(table)))
    table = table[0]
    # Complain if the element isn't a table element.
    if table.tag != "table":
        click.UsageError("expression matched {} element, not table "
                         "element.".format(table.tag))

    # Output to stdout.
    rows = csv.writer(sys.stdout)
    # The convoluted XPath expression below is to stop nested tables being
    # flattened out in the output. We only want the table rows that are direct
    # children of the selected table to be output as rows. Any tables within
    # the selected table should be output as text within a row cell, not added
    # as distinct, top-level rows.
    for tr in table.xpath("./tr|./thead/tr|./tbody/tr|./tfoot/tr"):
        row = []
        # Loop through all th and td elements and output them as cells. Since
        # CSV doesn't have any concept of headers or data cells we don't need
        # to treat them differently.
        for cell in tr.xpath("./th|./td"):
            # Strip whitespace, convert null values to None, and append all the
            # text within the cell element and its children to the row,
            text = " ".join(cell.text_content().split())
            if text.lower() in null_value:
                text = None
            elif convert_numbers:
                currency_symbol = currency_symbol or DEFAULT_CURRENCY_SYMBOLS
                try:
                    text = numberise(text, group_symbol, decimal_symbol,
                                     currency_symbol)
                except ValueError:
                    pass  # String not numeric, leave as-is.
            row.append(text)
        if any(row):
            # Only output a row if it has at least one non-empty cell.
            rows.writerow(row)


if __name__ == "__main__":
    main()
