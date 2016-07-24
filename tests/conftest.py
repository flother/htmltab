import pytest


@pytest.fixture(scope="session")
def basic_csv():
    with open("tests/fixtures/basic.csv") as fh:
        file_contents = fh.read()
    return file_contents
