import click.testing

from htmltab.cli import main


def test_local_file(basic_csv):
    """
    Test that the correct CSV data is output when using a local HTML5
    document as input.
    """
    runner = click.testing.CliRunner()
    result = runner.invoke(main, ["tests/fixtures/basic.html"])
    assert result.exit_code == 0
    assert result.output == basic_csv
