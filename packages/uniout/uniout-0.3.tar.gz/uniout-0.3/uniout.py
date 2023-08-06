#!/usr/bin/env python
# -*- coding: utf-8 -*-

from _uniout import __version__, Uniout, runs_in_ipython

if runs_in_ipython():
    from IPython.utils import io
    io.stdout = Uniout(sys.stdout)
    io.stderr = Uniout(sys.stderr)
else:
    import sys
    sys.stdout = Uniout(sys.stdout)
    sys.stderr = Uniout(sys.stderr)
