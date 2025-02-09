# Contributing

HTMLTab is an open-source project and contributions are welcome.

## Setting up a development environment

HTMLTab is written in Python and uses [uv](https://docs.astral.sh/uv/) for project management. [Install uv](https://docs.astral.sh/uv/getting-started/installation/) before you do anything else.

[Create a fork of HTMLTab](https://github.com/flother/htmltab/fork) under your own GitHub account, and then clone that repo on your computer:

```term
git clone git@github.com:YOURNAME/htmltab
```

!!! note
    If you want to get started without creating a fork, clone the original repo instead:

        git clone git@github.com:flother/htmltab

Now you can use uv to create a virtual environment:

```term
uv venv --python 3.12
```

And then install the project's dependencies:

```term
uv sync
```

Once that's complete, activate the virtual environment:

```term
source .venv/bin/activate
```

Now you're ready to start developing! You can run HTMLTab, and any changes you make will be reflected in the command-line program:

```
htmltab --help
```
