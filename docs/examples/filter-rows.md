# Filter rows in an output CSV

You can use HTMLTab in combination with [xsv](https://github.com/BurntSushi/xsv) to output only those rows within a table that match a string or regular expression. For example, to get a list of countries whose entire sovereignty is disputed by another state, run:

```term
htmltab --select 2 https://en.wikipedia.org/wiki/List_of_sovereign_states \
    | xsv search -s 3 "None" --invert-match \
    | xsv select 1
```

1. `htmltab --select 2` selects the second `<table>` element on the Wikipedia page, and converts it to CSV
2. `xsv search --select 3 --invert-match "None"` filters out all CSV rows where the third column contains `None`
3. `xsv select 1` extracts only the first column from the remaining data.

As of the time of writing, that command outputs:

```text
Common and formal names
Armenia – Republic of Armenia
China – People's Republic of China[o]
Cyprus – Republic of Cyprus
Israel – State of Israel
North Korea – Democratic People's Republic of Korea
Palestine – State of Palestine
South Korea – Republic of Korea
```
