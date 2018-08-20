#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from black import format_str


class BlackFormatter(object):
    def __init__(self, ip):
        self.shell = ip

    def format(self, result):
        cell = result.info.raw_cell
        try:
            cell = re.sub(r"^\s*([!%?])", "# :@BF@: \g<1>", cell)
            cell = format_str(src_contents=cell, line_length=88)
            cell = re.sub(r"^#\s*:@BF@:\s*([!%?])", "\g<1>", cell)
            self.shell.set_next_input(cell.rstrip(), replace=True)
        except ValueError:
            pass


black_formatter = None


def load_ipython_extension(ip):
    global black_formatter
    if not black_formatter:
        black_formatter = BlackFormatter(ip)
        ip.events.register("post_run_cell", black_formatter.format)


def unload_ipython_extension(ip):
    global black_formatter
    if black_formatter:
        ip.events.unregister("post_run_cell", black_formatter.format)
        black_formatter = None
