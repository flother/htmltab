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


DEFAULT_NULL_VALUES = ("na", "n/a", ".", "-")


@click.command()
@click.option("--css", "-s", "language", flag_value="css", default=True,
              help="Interpret EXPRESSION as a CSS selector (default).")
@click.option("--xpath", "-x", "language", flag_value="xpath",
              help="Interpret EXPRESSION as an XPath expression.")
@click.option("--index", "-i", "language", flag_value="index",
              help="Interpret EXPRESSION as an index, starting from 1.")
@click.option("--null-value", "-n", multiple=True,
              help="Case-insensitive value to convert to an empty cell in the "
                   "CSV output (defaults are '{}')".format(
                       "', '".join(DEFAULT_NULL_VALUES)))
@click.argument("expression")
@click.argument("html_file", type=click.File("rb"))
def main(language, null_value, expression, html_file):
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

    # Read the HTML file using lxml's HTML parser, but convert to Unicode using
    # Beautiful Soup's UnicodeDammit class.
    try:
        unicode_html = UnicodeDammit(html_file.read())
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
            row.append(text)
        if any(row):
            # Only output a row if it has at least one non-empty cell.
            rows.writerow(row)


if __name__ == "__main__":
    main()
