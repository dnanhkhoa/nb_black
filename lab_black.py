# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import re
import sys

from IPython.display import Javascript, display

if sys.version_info >= (3, 6, 0):
    from black import format_str, FileMode

    def _format_code(code):
        return format_str(src_contents=code, mode=FileMode())


else:
    from yapf.yapflib.yapf_api import FormatCode

    def _format_code(code):
        return FormatCode(code, style_config="facebook")[0]


class BlackFormatter(object):
    def __init__(self, ip, is_lab):
        self.shell = ip
        self.is_lab = is_lab

    def __set_cell(self, cell, cell_id=None):
        if self.is_lab:
            self.shell.set_next_input(cell, replace=True)
        else:
            js_code = """
            setTimeout(function() {
                var nbb_cell_id = {};
                var nbb_formatted_code = {};
                var nbb_cells = Jupyter.notebook.get_cells();
                for (var i = 0; i < nbb_cells.length; ++i) {
                    if (nbb_cells[i].input_prompt_number == nbb_cell_id) {
                        nbb_cells[i].set_text(nbb_formatted_code);
                        break;
                    }
                }
            }, 500);
            """
            display(Javascript(js_code.format(cell_id, json.dumps(cell))))

    def format_cell(self, *args, **kwargs):
        try:
            cell_id = len(self.shell.user_ns["In"]) - 1
            if cell_id > 0:
                transformed_cell = self.shell.user_ns["In"][cell_id]

                formatted_code = _format_code(transformed_cell)

                # Reverse magic functions

                self.__set_cell(formatted_code.strip(), cell_id)
        except (ValueError, TypeError, AssertionError) as err:
            logging.exception(err)


black_formatter = None


def load_ipython_extension(ip):
    global black_formatter
    if black_formatter is None:
        black_formatter = BlackFormatter(ip, is_lab=True)
        ip.events.register("post_run_cell", black_formatter.format_cell)


def unload_ipython_extension(ip):
    global black_formatter
    if black_formatter:
        ip.events.unregister("post_run_cell", black_formatter.format_cell)
        black_formatter = None
