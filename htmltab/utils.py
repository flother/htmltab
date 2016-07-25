from decimal import Decimal, InvalidOperation
import urllib.parse

from bs4 import UnicodeDammit
from click.types import File
from lxml.cssselect import SelectorError
from lxml.etree import LxmlError
import lxml.html

from .types import URL


def open_file_or_url(ctx, param, value):
    """
    Click option callback to handle an option that can either be a local
    file or an HTTP/HTTPS URL.
    """
    scheme = urllib.parse.urlparse(value).scheme
    if scheme in ("http", "https"):
        return lambda: URL().convert(value, param, ctx).text
    else:
        return lambda: File("rb").convert(value, param, ctx).read()


def parse_html(html_file):
    """
    Read the HTML file using lxml's HTML parser, but convert to Unicode
    using Beautiful Soup's UnicodeDammit class.

    Can raise LxmlError or TypeError if the file can't be opened or
    parsed.
    """
    unicode_html = UnicodeDammit(html_file, smart_quotes_to="html",
                                 is_html=True)
    if unicode_html.unicode_markup is None:
        raise ValueError("no HTML provided")
    if not unicode_html.unicode_markup:
        raise ValueError("could not detect character encoding")
    return lxml.html.fromstring(unicode_html.unicode_markup)


def select_elements(doc, select):
    """
    Return the elements within ``doc`` that match the selector
    ``select``. The selector can be an index, a CSS selector, or an
    XPath expression.
    """
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
            except LxmlError:
                # Catch the specific LXML error and raise a more generic error
                # because the problem could lie with any of the index, CSS
                # selector, or XPath expression.
                raise ValueError("'{}' not an index, CSS selector, or XPath "
                                 "expression".format(select))
    return elements


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
