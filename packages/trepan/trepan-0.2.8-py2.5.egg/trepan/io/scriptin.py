# -*- coding: utf-8 -*-
#   Copyright (C) 2009 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Debugger Script input interface. """

import types

from import_relative import import_relative, get_srcdir
Mbase = import_relative('base', top_name='trepan')

# Do we need this?
class ScriptInput(Mbase.DebuggerInputBase):
    """Debugger Script input - largely the same as DebuggerInput."""

    def __init__(self, inp, opts=None):

        self.input     = None
        self.line_edit = False # Our name for GNU readline capability
        self.name      = None
        self.open(inp, opts)
        return

    def close(self):
        if self.input:
            self.input.close()
            pass
        return

    def open(self, inp, opts=None):
        """Use this to set what file to read from. """
        if isinstance(inp, types.FileType):
            self.input = inp
        elif isinstance(inp, types.StringType):
            self.name  = inp
            self.input = open(inp, 'r')
        else:
            raise IOError, ("Invalid input type (%s) for %s" % (type(inp),
                                                                inp))
        return

    def readline(self, prompt='', use_raw=None):
        """Read a line of input. Prompt and use_raw exist to be
        compatible with other input routines and are ignored.
        EOFError will be raised on EOF.
        """
        line = self.input.readline()
        if not line: raise EOFError
        return line.rstrip("\n")

# Demo
if __name__=='__main__':
    inp = ScriptInput('scriptin.py')
    line = inp.readline()
    print(line)
    inp.close()
    # Note opts below are aren't acted upon. They are there for
    # compatibility
    import os
    my_file = os.path.join(get_srcdir(), 'scriptin.py')
    inp.open(my_file, opts={'use_raw': False})
    while True:
        try:
            inp.readline()
        except EOFError:
            break
        pass
    try:
        inp.readline()
    except EOFError:
        print('EOF handled correctly')
    pass
