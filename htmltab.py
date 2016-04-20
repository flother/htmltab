"""
Command-line utility to parse an HTML document, find a particular
``table`` element within the document, convert the table to CSV, and
output the CSV to ``stdout``.
"""
import csv
import sys

import click
import lxml.etree
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
    # Read the HTML file using lxml's default parser.
    try:
        doc = lxml.etree.HTML(html_file.read())
    except lxml.etree.LxmlError:
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
