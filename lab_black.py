#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import sys
from distutils.version import LooseVersion

import IPython

if sys.version_info >= (3, 6, 0):
    from black import format_str, FileMode


    def _format_code(code):
        return format_str(src_contents=code, mode=FileMode())


else:
    from yapf.yapflib.yapf_api import FormatCode


    def _format_code(code):
        return FormatCode(code, style_config="facebook")[0]


class BlackFormatter(object):
    def __init__(self, ip):
        self.shell = ip

    if LooseVersion(IPython.__version__) < LooseVersion("6.5"):

        def format(self):
            try:
                inp_id = len(self.shell.user_ns["In"]) - 1
                if inp_id > 0:
                    cell = self.shell.user_ns["_i%d" % inp_id]

                    # Skip if exists magic command `load`
                    if re.search(r"^[ \t]*%load +", cell, flags=re.M):
                        return

                    cell = re.sub(r"^(\s*[!%?])", "# :@BF@: \g<1>", cell, flags=re.M)
                    cell = _format_code(cell)
                    cell = re.sub(r"^\s*# :@BF@: (\s*[!%?])", "\g<1>", cell, flags=re.M)
                    self.shell.set_next_input(cell.rstrip(), replace=True)
            except (ValueError, TypeError) as e:
                logging.exception(e)

    else:

        def format(self, result):
            try:
                cell = result.info.raw_cell

                # Skip if exists magic command `load`
                if re.search(r"^[ \t]*%load +", cell, flags=re.M):
                    return

                cell = re.sub(r"^(\s*[!%?])", "# :@BF@: \g<1>", cell, flags=re.M)
                cell = _format_code(cell)
                cell = re.sub(r"^\s*# :@BF@: (\s*[!%?])", "\g<1>", cell, flags=re.M)
                self.shell.set_next_input(cell.rstrip(), replace=True)
            except (ValueError, TypeError) as e:
                logging.exception(e)


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
