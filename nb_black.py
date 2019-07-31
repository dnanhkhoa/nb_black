# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from lab_black import BlackFormatter, black_formatter, unload_ipython_extension


def load_ipython_extension(ip):
    global black_formatter
    if black_formatter is None:
        black_formatter = BlackFormatter(ip, is_lab=False)
        ip.events.register("post_run_cell", black_formatter.format_cell)
