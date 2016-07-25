from httmock import HTTMock, all_requests

from htmltab.cli import main


@all_requests
def basic_response(url, request):
    with open("tests/fixtures/basic.html") as fh:
        file_contents = fh.read()
    return {"status_code": 200,
            "text": file_contents,
            "content": file_contents}


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
