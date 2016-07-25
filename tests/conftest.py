import click.testing
import pytest


@pytest.fixture(scope="session")
def runner():
    return click.testing.CliRunner()


@pytest.fixture(scope="session")
def basic_csv():
    with open("tests/fixtures/basic.csv") as fh:
        file_contents = fh.read()
    return file_contents


@pytest.fixture(scope="session")
def three_csv_table_one():
    with open("tests/fixtures/three_table1.csv") as fh:
        file_contents = fh.read()
    return file_contents


@pytest.fixture(scope="session")
def three_csv_table_two():
    with open("tests/fixtures/three_table2.csv") as fh:
        file_contents = fh.read()
    return file_contents


@pytest.fixture(scope="session")
def three_csv_table_three():
    with open("tests/fixtures/three_table3.csv") as fh:
        file_contents = fh.read()
    return file_contents
