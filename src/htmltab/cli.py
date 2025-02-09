"""
Command-line utility to parse an HTML document, find a particular
``table`` element within the document, convert the table to CSV, and
output the CSV to ``stdout``.
"""

import contextlib
import csv
from decimal import Decimal
from typing import IO, Any, Callable

import click
from lxml.etree import LxmlError

from .utils import numberise, open_file_or_url, parse_html, select_elements

DEFAULT_NULL_VALUES = ["NA", "N/A", ".", "-"]
DEFAULT_CURRENCY_SYMBOLS = ["$", "¥", "£", "€"]

type Cell = None | Decimal | str
type Row = list[Cell]


@click.command()
@click.option(
    "--select",
    "-s",
    default="1",
    help="Integer index, CSS selector, or XPath expression that "
    "determines the table to convert to CSV.",
)
@click.option(
    "--null-value",
    "-n",
    multiple=True,
    help="Case-sensitive value to convert to an empty cell in the "
    "CSV output. Use multiple times if you have more than one "
    "null value.  [default: '{}']".format("', '".join(DEFAULT_NULL_VALUES)),
)
@click.option(
    "--convert-numbers/--keep-numbers",
    "-c/-k",
    is_flag=True,
    default=True,
    help="Convert number-like strings into numbers "
    "(e.g. remove group symbols, percent signs) "
    "or leave unchanged.  [default: convert]",
)
@click.option(
    "--group-symbol",
    "-g",
    default=",",
    show_default=True,
    help="Symbol used to group digits in numbers (e.g. the ',' in '1,000.00').",
)
@click.option(
    "--decimal-symbol",
    "-d",
    default=".",
    show_default=True,
    help="Symbol used to separate integer from fraction in numbers "
    "(e.g. the '.' in '1,000.00').",
)
@click.option(
    "--currency-symbol",
    "-u",
    multiple=True,
    help="Currency symbol to remove when converting number-like "
    "strings. Use multiple times if you have more than one "
    "currency symbol  [default: '{}']".format("', '".join(DEFAULT_CURRENCY_SYMBOLS)),
)
@click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default="-",
    help="Write output to file instead of stdout",
)
@click.argument("html_file", callback=open_file_or_url, default="-")
@click.version_option()
def main(
    select: str,
    null_value: list[str],
    convert_numbers: bool,
    group_symbol: str,
    decimal_symbol: str,
    currency_symbol: list[str],
    output: IO[Any],
    html_file: Callable[[], str],
):
    """
    <https://flother.github.io/htmltab>

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

    The CSV data will be output to stdout unless the '--output' option
    is specified.
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

    # Parse file contents as HTML.
    try:
        doc = parse_html(html_file())
    except ValueError as err:
        raise click.UsageError(str(err))
    except (LxmlError, TypeError):
        raise click.UsageError("could not parse HTML")

    # Select the elements that the user's interested in.
    try:
        elements = select_elements(doc, select)
    except ValueError as err:
        raise click.BadParameter(str(err))

    # Acceptable inputs are a single table element, or a collection of one or
    # more tr elements. Anything else is considered bad input.
    if len(elements) == 0:
        raise click.UsageError("value matched no elements")
    elif len(elements) == 1 and elements[0].tag == "table":
        # The convoluted XPath expression below is to stop nested tables being
        # flattened out in the output. We only want the table rows that are
        # direct children of the selected table to be output as rows. Any
        # tables within the selected table should be output as text within a
        # row cell, not added as distinct, top-level rows.
        elements = elements[0].xpath("./tr|./thead/tr|./tbody/tr|./tfoot/tr")
    elif len(elements) == 1 and elements[0].tag != "tr":
        raise click.UsageError(f"select value matched {elements[0].tag} element")
    elif any(el.tag != "tr" for el in elements):
        raise click.UsageError(
            "select value must match one 'table' element or one or more 'tr' elements"
        )

    # Use the set of default null values if the user didn't specify any. When a
    # cell value matches one of these it will be output as an empty cell in the
    # CSV.
    null_value = null_value or DEFAULT_NULL_VALUES
    # If the user didn't specify at least one currency symbol, use the default
    # set.
    currency_symbol = currency_symbol or DEFAULT_CURRENCY_SYMBOLS

    rows: list[Row] = []
    num_columns = 0  # Holds the cell length of the longest row.
    for tr in elements:
        row: Row = []
        cell: Cell = None
        # Loop through all th and td elements and output them as cells. Since
        # CSV doesn't have any concept of headers or data cells we don't need
        # to treat them differently.
        for cell_element in tr.xpath("./th|./td"):
            # Strip whitespace, convert null values to None, and append all the
            # text within the cell element and its children to the row,
            cell = " ".join(cell_element.text_content().split())
            if cell in null_value:
                cell = None
            elif convert_numbers:
                with contextlib.suppress(ValueError):
                    # ValueError means the string isn't numeric, so leave it as-is.
                    cell = numberise(
                        cell, group_symbol, decimal_symbol, currency_symbol
                    )
            # Parse the colspan attribute. A cell's value is used as an
            # individual cell in the output row once for every column it's
            # meant to span. If ``colspan=4`` then the cell's value will be
            # output four times in the row. Regarding the value of the colspan
            # attribute, the HTML5 spec is followed here, with only integer
            # values greater than zero allowed.
            try:
                col_span = cell_element.attrib["colspan"]
                if col_span.isdigit():
                    col_span = int(col_span)
                else:
                    # Ignore negative values and non-integers, as per HTML5.
                    raise ValueError(f"invalid integer {col_span}")
                # Zero as a value becomes 1, as per HTML5 spec.
                if col_span == 0:
                    col_span = 1
            except (KeyError, TypeError, ValueError):
                # HTML 5 says (sensibly) that the default value is 1.
                col_span = 1
            row += [cell] * col_span
        if any(row):
            if len(row) > num_columns:
                # This is the row with the largest number of cells so far, so
                # store the number of columns it contains. This is used when
                # outputting the CSV to stdout to ensure all rows are the same
                # length.
                num_columns = len(row)
            # Only include a row in the output if it has at least one non-empty
            # cell.
            rows.append(row)

    # Output the CSV to stdout.
    out = csv.writer(output)
    for row in rows:
        # Extra empty cells are added to the row as required, to ensure that
        # all rows have the same number of fields (as required by the closest
        # thing CSV has to a specification, RFC 4180).
        out.writerow(row + ([""] * (num_columns - len(row))))
