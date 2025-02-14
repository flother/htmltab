# HTMLTab documentation

HTMLTab is a command-line utility that parses an HTML document (from a URL or a local file), picks out a `<table>` element of your choosing, and converts it to CSV data.

With HTMLTab you can:

- Convert an HTML table into CSV data in a single command
- Pick which table within the to convert using a CSS selector, XPath expression, or integer index
- Remove percent signs and currency symbols from numbers
- Convert number-like strings into integer or float values (e.g. convert `1.000.000,00` to `1000000.00`)
- Define what counts as a null value
- Save the CSV data to a file

HTMLTab is written in Python. To use it you'll need Python version 3.12 or higher installed on your system. Visit Real Python for a [step-by-step guide for installing Python](https://realpython.com/installing-python/) on your operating system.

## Installation

The recommended method of installation is to use [Pipx](https://pypa.github.io/pipx/) to install HTMLTab system-wide:

```sh
pipx install git+https://github.com/flother/htmltab
```

Once installation is complete the `htmltab` command will be available to you in your favourite shell.

If you can't use Pipx you can install HTMLTab using Python's standard package manager, [Pip](https://pip.pypa.io/en/stable/). Ideally, you should install HTMLTab in a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/).

```sh
pip install git+https://github.com/flother/htmltab#egg=htmltab
```

Once installation is complete the `htmltab` command will be available while the virtual environment is active.

To find out how to use the `htmltab` command, see the [CLI reference](usage.md).

## Quick start

If you want to convert the first table in a webpage into CSV data, you simply need to pass the URL to HTMLTab. Let's say you want to see the latest standings in the English Premier League. We can easily get that from [The Guardian's league table page](https://www.theguardian.com/football/premierleague/table):

```sh
htmltab https://www.theguardian.com/football/premierleague/table
```

Running that will output that page's copy of the league table as a CSV:

```csv
P,Team,GP,W,D,L,F,A,GD,Pts,Form
1,Man City,21,17,2,2,53,13,40,53,Won against Leeds Won against Newcastle Won against Leicester Won against Brentford Won against Arsenal
2,Chelsea,21,12,7,2,45,16,29,43,Drew with Everton Drew with Wolves Won against Aston Villa Drew with Brighton Drew with Liverpool
3,Liverpool,20,12,6,2,52,18,34,42,Won against Aston Villa Won against Newcastle Drew with Spurs Lost to Leicester Drew with Chelsea
4,Arsenal,20,11,2,7,33,25,8,35,Won against Southampton Won against West Ham Won against Leeds Won against Norwich Lost to Man City
5,West Ham,20,10,4,6,37,27,10,34,Drew with Burnley Lost to Arsenal Lost to Southampton Won against Watford Won against C Palace
6,Spurs,18,10,3,5,23,20,3,33,Won against Norwich Drew with Liverpool Won against C Palace Drew with Southampton Won against Watford
7,Man Utd,19,9,4,6,30,27,3,31,Won against C Palace Won against Norwich Drew with Newcastle Won against Burnley Lost to Wolves
8,Wolves,19,8,4,7,14,14,0,28,Lost to Liverpool Lost to Man City Won against Brighton Drew with Chelsea Won against Man Utd
9,Brighton,19,6,9,4,20,20,0,27,Drew with Southampton Lost to Wolves Won against Brentford Drew with Chelsea Won against Everton
10,Leicester,18,7,4,7,31,33,-2,25,Drew with Southampton Lost to Aston Villa Won against Newcastle Lost to Man City Won against Liverpool
11,C Palace,20,5,8,7,29,30,-1,23,Won against Everton Drew with Southampton Lost to Spurs Won against Norwich Lost to West Ham
12,Brentford,19,6,5,8,23,26,-3,23,Drew with Leeds Won against Watford Lost to Brighton Lost to Man City Won against Aston Villa
13,Aston Villa,19,7,1,11,25,30,-5,22,Won against Leicester Lost to Liverpool Won against Norwich Lost to Chelsea Lost to Brentford
14,Southampton,19,4,9,6,20,29,-9,21,Drew with Brighton Lost to Arsenal Drew with C Palace Won against West Ham Drew with Spurs
15,Everton,18,5,4,9,23,32,-9,19,Lost to Liverpool Won against Arsenal Lost to C Palace Drew with Chelsea Lost to Brighton
16,Leeds,19,4,7,8,21,37,-16,19,Drew with Brentford Lost to Chelsea Lost to Man City Lost to Arsenal Won against Burnley
17,Watford,18,4,1,13,22,36,-14,13,Lost to Chelsea Lost to Man City Lost to Brentford Lost to West Ham Lost to Spurs
18,Burnley,17,1,8,8,16,27,-11,11,Drew with Wolves Lost to Newcastle Drew with West Ham Lost to Man Utd Lost to Leeds
19,Newcastle,19,1,8,10,19,42,-23,11,Won against Burnley Lost to Leicester Lost to Liverpool Lost to Man City Drew with Man Utd
20,Norwich,19,2,4,13,8,42,-34,10,Lost to Spurs Lost to Man Utd Lost to Aston Villa Lost to Arsenal Lost to C Palace
```

You can save the CSV data to a file with the `--output` flag:

```sh
htmltab https://www.theguardian.com/football/premierleague/table --output epl.csv
```

HTMLTab is useful in combination with other tools. We can use the standard Unix tool `head` to show only the top six teams and format the table with [xsv](https://github.com/BurntSushi/xsv), removing the wordy "Form" column in the process:

```sh
$ htmltab https://www.theguardian.com/football/premierleague/table | head -n 7 | xsv select "!Form" | xsv table
P   Team       GP  W   D   L   F   A   GD  Pts
1   Man City   21  17  2   2   53  13  40  53
2   Chelsea    21  12  7   2   45  16  29  43
3   Liverpool  20  12  6   2   52  18  34  42
4   Arsenal    20  11  2   7   33  25  8   35
5   West Ham   20  10  4   6   37  27  10  34
6   Spurs      18  10  3   5   23  20  3   33
```

We could combine HTMLTab with [Miller](https://miller.readthedocs.io/) to find out how many goals have been scored this season:

```sh
$ htmltab https://www.theguardian.com/football/premierleague/table | mlr --icsv put -q '@goals += $F; end { emit @goals }'
goals=544
```

!!! tip
    Because The Guardian's page contains live league data, your results will probably differ from the data above.

## What next?

- [See more examples](examples/filter-rows.md)
- [Read the CLI reference](usage.md)
- [Set up a development environment](contributing.md)
