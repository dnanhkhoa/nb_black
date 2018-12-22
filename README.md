# nb_black

[![PyPI](https://img.shields.io/pypi/v/nb_black.svg)]()
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nb_black.svg)]()

A simple extension for Jupyter Notebook and Jupyter Lab to beautify Python code automatically using **Black**.

Please note that since the **Black** package only supports Python 3.6+, so **YAPF** package will be used for the lower versions. And please **DO NOT EDIT** your code while running cell, otherwise your new code will be replaced by the formatted code.

## Installation

You can install this package using [pip](http://www.pip-installer.org):

```
$ [sudo] pip install nb_black
```

## Usage

For Jupyter Notebook:

```
%load_ext nb_black
```

For Jupyter Lab:

```
%load_ext lab_black
```

Just put this code into the first cell in your Notebook, and that's all. :)
