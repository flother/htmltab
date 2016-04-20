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
@click.option("--css", "language", flag_value="css", default=True,
              help="Use a CSS selector to determine the table (default).")
@click.option("--xpath", "language", flag_value="xpath",
              help="Use an XPath expression to determine the table.")
@click.option("--index", "language", flag_value="index",
              help="Use an index, starting from 1, to determine the table.")
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
    for row in table.xpath(".//tr"):
        rows.writerow([cell.text
                       if cell.text and cell.text.lower() not in null_value
                       else None
                       for cell in row.xpath("./th|./td")
                       ])


if __name__ == "__main__":
    main()
