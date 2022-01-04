# HTMLTab

[![Results from latest push build](https://github.com/flother/htmltab/actions/workflows/run_tests.yml/badge.svg)](https://github.com/flother/htmltab/actions)
[![Code coverage report](https://codecov.io/gh/flother/htmltab/branch/master/graph/badge.svg)](https://codecov.io/gh/flother/htmltab)

HTMLTab is a command-line utility to select a table within an HTML document and convert it to CSV. Here we can get the foreign-born population of Edinburgh from Wikipedia:

```sh
$ htmltab --select p+table.wikitable.plainrowheaders https://en.wikipedia.org/wiki/Edinburgh
Place of birth,Estimated resident population (2011)[117]
Poland,11651
India,4888
Ireland,4743
Mainland China [A],4188
United States,3700
Germany,3500
Pakistan,2472
Australia,2100
France,2000
Spain,2000
South Africa,1800
Canada,1800
Hong Kong,1600
```

For further details on installation and usage, see [HTMLTab's online documentation](https://flother.github.io/htmltab). If you find a bug or have a feature request, please [create an issue](https://github.com/flother/htmltab/issues).
