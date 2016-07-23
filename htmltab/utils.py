from decimal import Decimal, InvalidOperation
import urllib.parse

import click

from .types import URL


def open_file_or_url(ctx, param, value):
    """
    Click option callback to handle an option that can either be a local
    file or an HTTP/HTTPS URL.
    """
    scheme = urllib.parse.urlparse(value).scheme
    if scheme in ("http", "https"):
        return URL().convert(value, param, ctx).text
    else:
        return click.File("rb").convert(value, param, ctx).read()


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
