# Command-line usage

The basic form to invoke HTMLTab from the command-line is:

```sh
htmltab [OPTIONS] [HTML_DOCUMENT]
```

The options are, of course, optional but you must supply an HTML document as input.

## Supplying an input HTML document

You can pass an HTML document to HTMLTab in three different ways:

- A local file
- A remote URL
- A stream from `stdin`

### Local file

Say you have a file named `data.html` in the current directory. You can pass that to HTMLTab with:

```sh
htmltab data.html
```

All the usual filepath shortcuts are supported: `.` for the current directory, `..` for the parent directory, `~` for your home directory, `~rebecca` for Rebecca's home directory.

### Remote URL

If you want HTMLTab to request a remote URL and parse the returned HTML, use a similar invocation:

```sh
htmltab https://www.example.com/data.html
```

HTMLTab supports `http://` and `https://` URLs. If a URL returns an `HTTP 4xx` or `HTTP 5xx` error --- for example, `HTTP 404 Not Found` --- HTMLTab will exit with an error. HTMLTab will only make `GET` requests. If you need to use any other method you can stream from `stdin`.

### Streaming from `stdin`

If you want to read from standard input (`stdin`), use `-` as the HTML document. Using a Unix pipe to pass the output of a `POST` request made by [curl](https://curl.se/) into HTMLTab:

```sh
curl -X POST https://www.example.com/data.html | htmltab -
```

Or reading from a [here string](https://en.wikipedia.org/wiki/Here_document#Here_strings):

```sh
htmltab - <<< "<table><tr><td>1</td><td>2</td></tr></table>"
```

In fact, `-` is the default value for the input HTML document, so you don't need to include it explicitly if you're using `stdin`. The following two examples are equivalent to the two directly above.

```sh
curl -X POST https://www.example.com/data.html | htmltab
```

```sh
htmltab <<< "<table><tr><td>1</td><td>2</td></tr></table>"
```

## Options

You can use command-line options to modify the operation of the command.

### `--select`

The `--select` option is used when your input HTML document has multiple tables, and you want to convert a table that isn't the first table in the document. When that's the case you can use one of three methods of specifying the table:

- Integer index
- CSS selector
- XPath expression

#### Integer index

When you know you want the *n*th table in the HTML document, where *n* > 0, you can simply pass _n_ to `--select`. This is called the _integer index_ method. For example, if you have a local file `data.html` and you want to convert its third table to CSV, you can use:

```sh
htmltab --select 3 data.html
```

The integer index is one-based: `1` means the first table in the HTML document (as opposed to the second table as it would be in [zero-based numbering](https://en.wikipedia.org/wiki/Zero-based_numbering)). A zero or a negative value is an error.

#### CSS selector

Sometimes, over time, a table moves around within an HTML document. This is especially true when you're targetting a remote URL. One day the table may be the fourth within a document, the next it may be the fifth. In these cases you want to select the table by referencing the document structure. This is where CSS selectors or XPath expressions come in handy.

Let's say you're interested in an HTML document that contains weekly summarised data, and that table appears below other tables containing daily totals. On Mondays it's the second table in the document, on Tuesdays it's the third table in the document, and so on. Fortunately, the table has an `id` attribute with the value `weeklydata`. Using a [CSS selector](https://www.w3schools.com/cssref/css_selectors.asp), you can use that id to target the table wherever it appears in the document:

```sh
htmltab --select "#weeklydata" https://www.example.com/data.html
```

HTMLTab supports almost all CSS3 selectors. For further details see the documentation of the underlying [`cssselect`](https://cssselect.readthedocs.io/en/latest/#supported-selectors) library.

#### XPath expression

CSS selectors will probably be all you need, but in some complex cases you may need something more powerful. If that's the case you can use an [XPath expression](https://www.w3schools.com/xml/xpath_syntax.asp) as the value for `--select`. One example would be where you need the _last_ table in an HTML document:

```sh
htmltab --select "(//table)[last()]" https://www.example.com/data.html
```

#### Default value and short form

The default value of `--select` is `1`, which means the first table in the HTML document will be converted to CSV.

The short form of the `--select` option is `-s`.

### `--output`

Writes the CSV data output by HTMLTab to file instead of `stdout`.

```sh
htmltab data.html --output data.csv
```

The short form of this option is `-o`.

### `--keep-numbers`

Tells HTMLTab to leave any number-like values in the table unchanged (so, for example, currency symbols or percent signs will not be removed). This option turns off the default behaviour of converting number-like values.

```sh
$ htmltab --keep-numbers <<< '<table><tr><td>$1,000.00</td></tr></table>'
"$1,000.00"
```

This is the opposite of the `--convert-numbers` option. The two options cannot be used together.

The short form of this option is `-k`.

### `--convert-numbers`

Tells HTMLTab to convert number-like values in the table into integer or float values (for example, removing currency symbols or percent signs). This is the default behaviour and you shouldn't need to pass this option explicitly.

```sh
$ htmltab --convert-numbers <<< '<table><tr><td>$1,000.00</td></tr></table>'
1000.00
```

This is the opposite of the `--keep-numbers` option. The two options cannot be used together.

The short form of this option is `-c`.

### `--group-symbol`

Defines the character the HTML document uses to group digits in numbers (for example the `,` in `1,000,000`).

```sh
$ htmltab --group-symbol , <<< '<table><tr><td>1,000,000</td></tr></table>'
1000000
```

By default `,` is used as the grouping character. If you need to use a full stop as a grouping character, pass `--group-symbol .`.

The short form of this option is `-g`.

### `--decimal-symbol`

Defines the character the HTML document uses as the [decimal separator](https://en.wikipedia.org/wiki/Decimal_separator) (for example the `.` in `1000.00`).

```sh
$ htmltab --decimal-symbol , <<< '<table><tr><td>1000000,00</td></tr></table>'
100000000
```

By default `.` is used as the decimal separator. If you need to use a comma as a decimal separator, pass `--decimal-symbol ,`.

The short form of this option is `-d`.

### `--currency-symbol`

Defines the character to remove when converting number-like strings. You can pass the option multiple times if you have more than one currency symbol.

```sh
$ htmltab --currency-symbol ₹ <<< '<table><tr><td>10₹</td></tr></table>'
10
```

By default `$`, `¥`, `£`, and `€` considered to be currency symbols. These are not used if you pass your own currency symbols (unless you include them explicitly).

The short form of this option is `-u`.

### `--null-value`

Allows you to define a case-sensitive value to convert to an empty cell in the CSV output. You can pass the option multiple times if you have more than one null value.

```sh
htmltab data.html --null-value None --null-value NO
```

By default, `NA`, `N/A`, `.`, and `-` are considered null values. These are not used if you pass your own null value (unless you include them explicitly).

The short form of this option is `-n`.

### `--delimiter`

Let's you choose the character used to separate fields in the CSV output. By default a comma (`,`) is used as the delimiter. If you want to use a tab as a delimiter, pass `--delimiter $'\t'` (Bash and Zsh) or `--delimiter (printf '\t')` (Fish).

### `--version`

Show the version of HTMLTab you have installed, and exit.

### `--help`

Show a usage message --- essentially a short version of this page --- and exit.
