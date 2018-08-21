#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import re
import sys
from distutils.version import LooseVersion

import IPython
from IPython.display import display, Javascript

if sys.version_info >= (3, 6, 0):
    from black import format_str


    def _format_code(code):
        return format_str(src_contents=code, line_length=80)


else:
    from yapf.yapflib.yapf_api import FormatCode


    def _format_code(code):
        return FormatCode(code, style_config="facebook")[0]


class BlackFormatter(object):
    def __init__(self, ip):
        self.shell = ip
        self.js_code = """
        setTimeout(function() {
            var nbb_cell_id = %d;
            var nbb_formatted_code = %s;
            var nbb_cells = Jupyter.notebook.get_cells();
            for (var i = 0; i < nbb_cells.length; ++i) {
                if (nbb_cells[i].input_prompt_number == nbb_cell_id) {
                    nbb_cells[i].set_text(nbb_formatted_code);
                    break;
                }
            }
        }, 500);
        """

    def __format(self):
        try:
            inp_id = len(self.shell.user_ns["In"]) - 1
            if inp_id > 0:
                cell = self.shell.user_ns["_i%d" % inp_id]
                cell = re.sub(r"^(\s*[!%?])", "# :@BF@: \g<1>", cell, flags=re.M)
                cell = _format_code(cell)
                cell = re.sub(r"^\s*# :@BF@: (\s*[!%?])", "\g<1>", cell, flags=re.M)
                # noinspection PyTypeChecker
                display(Javascript(self.js_code % (inp_id, json.dumps(cell))))
        except (ValueError, TypeError):
            pass

    if LooseVersion(IPython.__version__) < LooseVersion("6.5"):

        def format(self):
            self.__format()

    else:

        def format(self, _):
            self.__format()


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
