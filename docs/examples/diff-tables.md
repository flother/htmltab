# Compare two CSV files and output only lines that differ

This guide shows you how to compare two CSV files and output the difference as a CSV file. As well as using HTMLTab it also uses `sdiff`, a standard tool on Linux and MacOS.

Let's say that yesterday you requested data from `https://example.com/data.csv` and saved it to a local file named `yesterday.csv`.

```term
htmltab https://example.com/data.csv > yesterday.csv
```

Today you can see the differences using:

```term
htmltab https://example.com/data.csv > today.csv
sdiff --suppress-common-lines yesterday.csv today.csv
```

That will use HTMLTab to get the fresh CSV data from the URL, save it as `today.csv`, and use `sdiff` to compare the new data against the old, suppressing any lines that haven't changed.

!!! tip
    If you're feeling adventurous, you can feed HTMLTab's output directly into `sdiff` without saving an intermediate file:

        sdiff --suppress-common-lines yesterday.csv <(htmltab https://example.com/data.csv)
