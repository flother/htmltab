import click.testing
from httmock import HTTMock, all_requests

from htmltab.cli import main


@all_requests
def basic_response(url, request):
    with open("tests/fixtures/basic.html") as fh:
        file_contents = fh.read()
    return {"status_code": 200,
            "text": file_contents,
            "content": file_contents}


def test_local_file(basic_csv):
    """
    Test that the correct CSV data is output when using a local HTML5
    document as input.
    """
    runner = click.testing.CliRunner()
    result = runner.invoke(main, ["tests/fixtures/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_csv


def test_url(basic_csv):
    runner = click.testing.CliRunner()
    with HTTMock(basic_response):
        result = runner.invoke(main, ["http://example.org/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_csv
