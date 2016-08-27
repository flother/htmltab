from decimal import Decimal

from httmock import HTTMock, all_requests
import pytest

from htmltab.cli import main
from htmltab.utils import numberise


@all_requests
def basic_response(url, request):
    with open("tests/fixtures/basic.html") as fh:
        file_contents = fh.read()
    return {"status_code": 200,
            "text": file_contents,
            "content": file_contents}


@all_requests
def response_404(url, request):
    return {"status_code": 404, "reason": "NOT FOUND"}


def test_local_file(runner, basic_csv):
    """
    Test that the correct CSV data is output when using a local HTML5
    document as input.
    """
    result = runner.invoke(main, ["tests/fixtures/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_csv


def test_url(runner, basic_csv):
    with HTTMock(basic_response):
        result = runner.invoke(main, ["http://example.org/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_csv


def test_zero_is_invalid_select_value(runner, three_csv_table_three):
    result = runner.invoke(main, ["-s", "0", "tests/fixtures/three.html"])
    assert result.exit_code != 0
    assert "Error: value matched no elements" in result.output


def test_integer_select_value(runner, three_csv_table_three):
    result = runner.invoke(main, ["--select", "3",
                                  "tests/fixtures/three.html"])
    assert result.output == three_csv_table_three
    result = runner.invoke(main, ["-s", "3", "tests/fixtures/three.html"])
    assert result.output == three_csv_table_three


def test_css_select_value(runner, three_csv_table_two):
    result = runner.invoke(main, ["--select", "#data table",
                                  "tests/fixtures/three.html"])
    assert result.output == three_csv_table_two
    result = runner.invoke(main, ["-s", "#data table",
                                  "tests/fixtures/three.html"])
    assert result.output == three_csv_table_two


def test_xpath_select_value(runner, three_csv_table_three):
    result = runner.invoke(main, ["--select", "(//table)[3]",
                                  "tests/fixtures/three.html"])
    assert result.output == three_csv_table_three
    result = runner.invoke(main, ["-s", "(//table)[3]",
                                  "tests/fixtures/three.html"])
    assert result.output == three_csv_table_three


def test_invalid_select_value(runner):
    result = runner.invoke(main, ["-s", "!", "tests/fixtures/three.html"])
    assert result.exit_code != 0
    assert "Error: Invalid value: '!'" in result.output


def test_table_rows_required(runner):
    result = runner.invoke(main, ["-s", "#data", "tests/fixtures/three.html"])
    assert result.exit_code != 0
    assert "Error: select value matched div element" in result.output

    result = runner.invoke(main, ["-s", "thead", "tests/fixtures/three.html"])
    assert result.exit_code != 0
    assert "Error:" in result.output


def test_table_rows_allowed(runner, three_csv_table_two):
    result = runner.invoke(main, ["--select", "#data table tr",
                                  "tests/fixtures/three.html"])
    assert result.exit_code == 0
    assert result.output == three_csv_table_two


def test_all_rows_are_same_length(runner, ragged_csv):
    result = runner.invoke(main, ["tests/fixtures/ragged.html"])
    assert result.exit_code == 0
    assert result.output == ragged_csv


def test_default_null_values(runner):
    result = runner.invoke(main, ["tests/fixtures/countries.html"])
    with open("tests/fixtures/countries_default_nulls.csv") as fh:
        file_contents = fh.read()
    assert result.exit_code == 0
    assert result.output == file_contents


def test_no_null_values(runner):
    # Setting "!" as the only null value means the default null values aren't
    # used and that "!" is the sole acceptable null value in the source table.
    result = runner.invoke(main, ["--null-value", "!",
                                  "tests/fixtures/countries.html"])
    with open("tests/fixtures/countries_no_nulls.csv") as fh:
        file_contents = fh.read()
    assert result.exit_code == 0
    assert result.output == file_contents


def test_custom_null_values(runner):
    with open("tests/fixtures/countries_custom_nulls.csv") as fh:
        file_contents = fh.read()
    result = runner.invoke(main, ["--null-value", "0", "--null-value", "na",
                                  "tests/fixtures/countries.html"])
    assert result.exit_code == 0
    assert result.output == file_contents
    result2 = runner.invoke(main, ["-n", "0", "-n", "na",
                                   "tests/fixtures/countries.html"])
    assert result.output == result2.output


def test_convert_numbers(runner, three_csv_table_two):
    # Test long option name.
    result = runner.invoke(main, ["-s", "2", "--convert-numbers",
                                  "tests/fixtures/three.html"])
    assert result.exit_code == 0
    assert result.output == three_csv_table_two
    # Test short option name.
    result2 = runner.invoke(main, ["-s", "2", "-c",
                                   "tests/fixtures/three.html"])
    assert result2.exit_code == 0
    assert result2.output == three_csv_table_two
    # Test that --convert-numbers is the default.
    result3 = runner.invoke(main, ["-s", "2", "tests/fixtures/three.html"])
    assert result3.exit_code == 0
    assert result3.output == three_csv_table_two


def test_keep_numbers(runner, three_csv_table_two_keep):
    # Test long option name.
    result = runner.invoke(main, ["-s", "2", "--keep-numbers",
                                  "tests/fixtures/three.html"])
    assert result.exit_code == 0
    assert result.output == three_csv_table_two_keep
    # Test short option name.
    result2 = runner.invoke(main, ["-s", "2", "-k",
                                   "tests/fixtures/three.html"])
    assert result2.exit_code == 0
    assert result2.output == three_csv_table_two_keep


def test_bad_input(runner):
    result = runner.invoke(main, input="<")
    assert result.exit_code != 0
    result2 = runner.invoke(main, input="<html></html>")
    assert result2.exit_code != 0


def test_404_response(runner):
    with HTTMock(response_404):
        result = runner.invoke(main, ["http://example.org/404.html"])
    assert result.exit_code != 0
    assert "HTTP 404 NOT FOUND (http://example.org/404.html)" in result.output


def test_group_symbol_and_decimal_mark(runner, basic_european_csv):
    """
    Test that the group symbol and decimal mark can be set using both
    long and short command-line options.
    """
    result = runner.invoke(main, ["--group-symbol",
                                  ".",
                                  "--decimal-symbol",
                                  ",",
                                  "tests/fixtures/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_european_csv

    result2 = runner.invoke(main, ["-g", ".", "-d", ",",
                                   "tests/fixtures/basic.html"])
    assert result2.exit_code == 0
    assert result2.output == result.output


def test_currency_symbol(runner, basic_eur_gbp):
    """
    Test that custom currency symbols can be set using a long and short
    command-line option.
    """
    result = runner.invoke(main, ["--currency-symbol", "€",
                                  "--currency-symbol", "£",
                                  "tests/fixtures/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_eur_gbp

    result2 = runner.invoke(main, ["-u", "€", "-u", "£",
                                   "tests/fixtures/basic.html"])
    assert result2.exit_code == 0
    assert result2.output == result.output


def test_numberise():
    currency_symbols = ("€", "$")
    with pytest.raises(ValueError):
        numberise("A", ",", ".", currency_symbols)
    assert Decimal("1") == numberise("1", ",", ".", currency_symbols)
    assert Decimal("1.23") == numberise("1.23", ",", ".", currency_symbols)
    assert Decimal("-50") == numberise("-50", ",", ".", currency_symbols)
    assert Decimal("-5.432") == numberise("-5.432", ",", ".", currency_symbols)

    assert Decimal("1") == numberise("€1", ",", ".", currency_symbols)
    assert Decimal("1.23") == numberise("€1.23", ",", ".", currency_symbols)
    assert Decimal("-1") == numberise("€-1", ",", ".", currency_symbols)
    assert Decimal("-1.23") == numberise("€-1.23", ",", ".", currency_symbols)

    assert Decimal("-1357.91") == numberise("-1,357.91", ",", ".",
                                            currency_symbols)
    assert Decimal("1357.91") == numberise("1,357.91", ",", ".",
                                           currency_symbols)

    assert Decimal("-1357.91") == numberise("-1.357,91", ".", ",",
                                            currency_symbols)
    assert Decimal("1357.91") == numberise("1.357,91", ".", ",",
                                           currency_symbols)
