"""
Command-line utility to parse an HTML document, find a particular
``table`` element within the document, convert the table to CSV, and
output the CSV to ``stdout``.
"""
import csv
from decimal import Decimal, InvalidOperation
import urllib.error
import urllib.parse
import urllib.request
import sys

from bs4 import UnicodeDammit
import click
from click.utils import safecall
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


class URL(click.ParamType):

    """
    Declare a parameter to be a URL as understood by ``urllib``. The URL
    is requested using the GET method and the connection is closed once
    the context is closed (the command finishes execution).
    """

    name = "url"

    def convert(self, value, param, ctx):
        """
        Opens the parameter value as a URL using
        ``urllib.request.urlopen``. A custom User-Agent header is used
        and a ten-second timeout is set, but otherwise no alterations
        are made to the defaults (i.e. no authentication, no cookies).
        Any error causes the command to fail.
        """
        try:
            request = urllib.request.Request(value)
            request.add_header("User-Agent",
                               "HTMLTab (+https://github.com/flother/htmltab)")
            response = urllib.request.urlopen(request, timeout=10)
            if ctx is not None:
                ctx.call_on_close(safecall(response.close))
        except urllib.error.HTTPError as err:
            self.fail("HTTP {} {} ({})".format(err.code, err.reason, value),
                      param, ctx)
        except urllib.error.URLError as err:
            self.fail("{} ({})".format(err.reason, value), param, ctx)
        return response


def open_file_or_url(ctx, param, value):
    """
    Click option callback to handle an option that can either be a local
    file or an HTTP/HTTPS URL.
    """
    scheme = urllib.parse.urlparse(value).scheme
    if scheme in ("http", "https"):
        return URL().convert(value, param, ctx)
    else:
        return click.File("rb").convert(value, param, ctx)


@click.command()
@click.option("--index", "-i", "language", flag_value="index", default=True,
              help="Interpret EXPRESSION as an index, starting from 1.")
@click.option("--css", "-s", "language", flag_value="css",
              help="Interpret EXPRESSION as a CSS selector.")
@click.option("--xpath", "-x", "language", flag_value="xpath",
              help="Interpret EXPRESSION as an XPath expression.")
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
@click.option("--currency-symbol", "-u", multiple=True,
              help="Currency symbol to remove when converting number-like "
                   "strings. Use multiple times if you have more than one "
                   "currency symbol  [default: '{}']".format("', '".join(
                       DEFAULT_CURRENCY_SYMBOLS)))
@click.argument("expression", default="1")
@click.argument("html_file", callback=open_file_or_url, default="-")
def main(language, null_value, convert_numbers, group_symbol, decimal_symbol,
         currency_symbol, expression, html_file):
    """
    Select a table within an HTML document and convert it to CSV. By
    default stdin will be used as input, but you can also pass a
    filename or a URL.

    EXPRESSION can be a number (using the '--index' option) that indexes
    a table in the HTML document, an XPath expression (using the
    '--xpath' option), or a CSS selector (using the '--css' option). By
    default '--index' is assumed, and the first table in the HTML
    document is used if no EXPRESSION is given.

    A table is defined as a single 'table' element, or a collection of
    one or more 'tr' elements. If a CSS selector or XPath expression
    matches anything else an error is returned.
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
            elements = doc.cssselect(expression)
        elif language == "xpath":
            elements = doc.xpath(expression)
        elif language == "index":
            if int(expression) == 0:
                raise click.BadParameter("indices start from 1")
            elements = doc.xpath("(//table)[{}]".format(int(expression)))
    except (SelectorError, lxml.etree.LxmlError, ValueError):
        # Either the CSS selector was invalid, the XPath expression was
        # invalid, or the index wasn't an integer.
        raise click.BadParameter(expression)

    # Acceptable inputs are a single table element, or a collection of one or
    # more tr elements. Anything else is considered bad input.
    if len(elements) == 0:
        raise click.UsageError("expression matched no elements.")
    elif len(elements) == 1 and elements[0].tag == "table":
        # The convoluted XPath expression below is to stop nested tables being
        # flattened out in the output. We only want the table rows that are
        # direct children of the selected table to be output as rows. Any
        # tables within the selected table should be output as text within a
        # row cell, not added as distinct, top-level rows.
        elements = elements[0].xpath("./tr|./thead/tr|./tbody/tr|./tfoot/tr")
    elif len(elements) == 1 and elements[0].tag != "tr":
        raise click.UsageError("expression matched {} element".format(
            elements[0].tag))
    elif any(el.tag != "tr" for el in elements):
        raise click.UsageError("expression must match one 'table' element or "
                               "one or more 'tr' elements")

    # Output to stdout.
    rows = csv.writer(sys.stdout)
    for tr in elements:
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
