#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from setuptools import setup


def readme(file_name):
    if os.path.isfile(file_name):
        with open(file_name, "r") as f:
            return f.read()


setup(
    name="nb_black",
    version="1.0.6",
    description="A simple extension for Jupyter Notebook and Jupyter Lab to beautify Python code automatically using Black.",
    long_description=readme(file_name="README.md"),
    keywords="black-formatter black-beautifier black jupyterlab-extension jupyter-notebook-extension",
    url="https://github.com/dnanhkhoa/nb_black",
    author="Khoa Duong",
    author_email="dnanhkhoa@live.com",
    license="MIT",
    py_modules=["nb_black", "lab_black"],
    zip_safe=False,
    install_requires=[
        "yapf >= '0.28'; python_version < '3.6'",
        "black >= '19.3'; python_version >= '3.6'",
        "ipython",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
