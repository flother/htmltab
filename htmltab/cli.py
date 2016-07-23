"""
Command-line utility to parse an HTML document, find a particular
``table`` element within the document, convert the table to CSV, and
output the CSV to ``stdout``.
"""
import csv
import sys

from bs4 import UnicodeDammit
import click
from lxml.etree import LxmlError
import lxml.html
from lxml.cssselect import SelectorError

from .utils import open_file_or_url, numberise


DEFAULT_NULL_VALUES = ("na", "n/a", ".", "-")
DEFAULT_CURRENCY_SYMBOLS = ("$", "¥", "£", "€")


@click.command()
@click.option("--select", "-s", default="1",
              help="Integer index, CSS selector, or XPath expression that "
                   "determines the table to convert to CSV.")
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
@click.argument("html_file", callback=open_file_or_url, default="-")
@click.version_option()
def main(select, null_value, convert_numbers, group_symbol, decimal_symbol,
         currency_symbol, html_file):
    """
    Select a table within an HTML document and convert it to CSV. By
    default stdin will be used as input, but you can also pass a
    filename or a URL.

    Unless otherwise specified, the first table element in the HTML
    document is converted to CSV. To change that behaviour pass an
    alternative using the '--select' option. The value may be an integer
    index, a CSS selector, or an XPath expression.

    To select the fourth table within the the file 'foo.html':

      htmltab --select 4 foo.html

    To select the table with the id 'data':

      htmltab --select table#data foo.html

    To select the rows within the second table inside the 'div' element
    with id 'bar', while excluding the rows in the header and footer:

      htmltab --select "(//div[@id='bar']//table)[2]/tbody/tr" foo.html
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
        unicode_html = UnicodeDammit(html_file, smart_quotes_to="html",
                                     is_html=True)
        if unicode_html.unicode_markup is None:
            raise click.UsageError("no HTML provided.")
        if not unicode_html.unicode_markup:
            raise click.UsageError("could not detect character encoding.")
        doc = lxml.html.fromstring(unicode_html.unicode_markup)
    except (LxmlError, TypeError):
        raise click.UsageError("could not parse HTML.")

    # Find the element(s) that match the index, CSS selector, or XPath
    # expression.
    try:
        int(select)
        elements = doc.xpath("(//table)[{}]".format(int(select)))
    except ValueError:
        # Expression wasn't a valid integer so try to use it as a CSS selector.
        try:
            elements = doc.cssselect(select)
        except SelectorError:
            # Nope, not a valid CSS expression. Last attempt is to try it as an
            # Path expression.
            try:
                elements = doc.xpath(select)
            except lxml.etree.LxmlError:
                # Send an error back to the user because their select value
                # isn't an integer, a CSS selector, or an XPath expression.
                raise click.BadParameter(select)

    # Acceptable inputs are a single table element, or a collection of one or
    # more tr elements. Anything else is considered bad input.
    if len(elements) == 0:
        raise click.UsageError("value matched no elements.")
    elif len(elements) == 1 and elements[0].tag == "table":
        # The convoluted XPath expression below is to stop nested tables being
        # flattened out in the output. We only want the table rows that are
        # direct children of the selected table to be output as rows. Any
        # tables within the selected table should be output as text within a
        # row cell, not added as distinct, top-level rows.
        elements = elements[0].xpath("./tr|./thead/tr|./tbody/tr|./tfoot/tr")
    elif len(elements) == 1 and elements[0].tag != "tr":
        raise click.UsageError("select value matched {} element".format(
            elements[0].tag))
    elif any(el.tag != "tr" for el in elements):
        raise click.UsageError("select value must match one 'table' element "
                               "or one or more 'tr' elements")

    # Use the set of default null values if the user didn't specify any. When a
    # cell value matches one of these it will be output as an empty cell in the
    # CSV.
    null_value = null_value or DEFAULT_NULL_VALUES

    # Output the CSV to stdout.
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
