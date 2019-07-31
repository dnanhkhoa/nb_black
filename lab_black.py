# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import re
import sys

from IPython.core.inputtransformer2 import (
    ESCAPE_DOUBLES,
    EscapedCommand,
    HelpEnd,
    MagicAssign,
    SystemAssign,
    TransformerManager,
    _help_end_re,
    assemble_continued_line,
    find_end_of_continued_line,
    tr,
)
from IPython.display import Javascript, display

__BF_SIGNATURE__ = "__BF_HIDDEN_VARIABLE_{}__"

if sys.version_info >= (3, 6, 0):
    from black import format_str, FileMode

    def _format_code(code):
        return format_str(src_contents=code, mode=FileMode())


else:
    from yapf.yapflib.yapf_api import FormatCode

    def _format_code(code):
        return FormatCode(code, style_config="facebook")[0]


def _transform_magic_commands(cell, hidden_variables):
    def __cell_magic(lines):
        # https://github.com/ipython/ipython/blob/1879ed27bb0ec3be5fee499ac177ad14a9ef7cfd/IPython/core/inputtransformer2.py#L91
        if not lines or not lines[0].startswith("%%"):
            return lines
        if re.match(r"%%\w+\?", lines[0]):
            # This case will be handled by help_end
            return lines
        magic_name, _, first_line = lines[0][2:-1].partition(" ")
        body = "".join(lines[1:])
        hidden_variables.append("".join(lines))
        return [__BF_SIGNATURE__.format(len(hidden_variables) - 1)]

    class __MagicAssign(MagicAssign):
        def transform(self, lines):
            # https://github.com/ipython/ipython/blob/1879ed27bb0ec3be5fee499ac177ad14a9ef7cfd/IPython/core/inputtransformer2.py#L223
            """Transform a magic assignment found by the ``find()`` classmethod.
            """
            start_line, start_col = self.start_line, self.start_col
            lhs = lines[start_line][:start_col]
            end_line = find_end_of_continued_line(lines, start_line)
            rhs = assemble_continued_line(lines, (start_line, start_col), end_line)
            assert rhs.startswith("%"), rhs
            magic_name, _, args = rhs[1:].partition(" ")

            lines_before = lines[:start_line]
            hidden_variables.append(rhs)
            call = __BF_SIGNATURE__.format(len(hidden_variables) - 1)
            new_line = lhs + call + "\n"
            lines_after = lines[end_line + 1 :]

            return lines_before + [new_line] + lines_after

    class __SystemAssign(SystemAssign):
        def transform(self, lines):
            # https://github.com/ipython/ipython/blob/1879ed27bb0ec3be5fee499ac177ad14a9ef7cfd/IPython/core/inputtransformer2.py#L262
            """Transform a system assignment found by the ``find()`` classmethod.
            """
            start_line, start_col = self.start_line, self.start_col

            lhs = lines[start_line][:start_col]
            end_line = find_end_of_continued_line(lines, start_line)
            rhs = assemble_continued_line(lines, (start_line, start_col), end_line)
            assert rhs.startswith("!"), rhs
            cmd = rhs[1:]

            lines_before = lines[:start_line]
            hidden_variables.append(rhs)
            call = __BF_SIGNATURE__.format(len(hidden_variables) - 1)
            new_line = lhs + call + "\n"
            lines_after = lines[end_line + 1 :]

            return lines_before + [new_line] + lines_after

    class __EscapedCommand(EscapedCommand):
        def transform(self, lines):
            # https://github.com/ipython/ipython/blob/1879ed27bb0ec3be5fee499ac177ad14a9ef7cfd/IPython/core/inputtransformer2.py#L382
            """Transform an escaped line found by the ``find()`` classmethod.
            """
            start_line, start_col = self.start_line, self.start_col

            indent = lines[start_line][:start_col]
            end_line = find_end_of_continued_line(lines, start_line)
            line = assemble_continued_line(lines, (start_line, start_col), end_line)

            if len(line) > 1 and line[:2] in ESCAPE_DOUBLES:
                escape, content = line[:2], line[2:]
            else:
                escape, content = line[:1], line[1:]

            if escape in tr:
                hidden_variables.append(line)
                call = __BF_SIGNATURE__.format(len(hidden_variables) - 1)
            else:
                call = ""

            lines_before = lines[:start_line]
            new_line = indent + call + "\n"
            lines_after = lines[end_line + 1 :]

            return lines_before + [new_line] + lines_after

    class __HelpEnd(HelpEnd):
        def transform(self, lines):
            # https://github.com/ipython/ipython/blob/1879ed27bb0ec3be5fee499ac177ad14a9ef7cfd/IPython/core/inputtransformer2.py#L439
            """Transform a help command found by the ``find()`` classmethod.
            """
            piece = "".join(lines[self.start_line : self.q_line + 1])
            indent, content = piece[: self.start_col], piece[self.start_col :]
            lines_before = lines[: self.start_line]
            lines_after = lines[self.q_line + 1 :]

            m = _help_end_re.search(content)
            if not m:
                raise SyntaxError(content)
            assert m is not None, content
            target = m.group(1)
            esc = m.group(3)

            # If we're mid-command, put it back on the next prompt for the user.
            next_input = None
            if (
                (not lines_before)
                and (not lines_after)
                and content.strip() != m.group(0)
            ):
                next_input = content.rstrip("?\n")

            hidden_variables.append(content)
            call = __BF_SIGNATURE__.format(len(hidden_variables) - 1)
            new_line = indent + call + "\n"

            return lines_before + [new_line] + lines_after

    transformer_manager = TransformerManager()
    transformer_manager.line_transforms = [__cell_magic]
    transformer_manager.token_transformers = [
        __MagicAssign,
        __SystemAssign,
        __EscapedCommand,
        __HelpEnd,
    ]
    return transformer_manager.transform_cell(cell)


def _recover_magic_commands(cell, hidden_variables):
    for hidden_variable_idx, hidden_variable in enumerate(hidden_variables):
        cell = cell.replace(
            __BF_SIGNATURE__.format(hidden_variable_idx), hidden_variable
        )
    return cell


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
            display(Javascript(js_code % (cell_id, json.dumps(cell))))

    def format_cell(self, *args, **kwargs):
        try:
            cell_id = len(self.shell.user_ns["In"]) - 1
            if cell_id > 0:
                cell = self.shell.user_ns["_i" + str(cell_id)]

                if re.search(r"^\s*%load(py)? ", cell, flags=re.M):
                    return

                hidden_variables = []

                # Transform magic commands into special variables
                cell = _transform_magic_commands(cell, hidden_variables)

                formatted_code = _format_code(cell)

                # Recover magic commands
                formatted_code = _recover_magic_commands(
                    formatted_code, hidden_variables
                )

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
