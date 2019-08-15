#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : test.py -- Test figures
# Author    : Juergen Hackl <hackl.research@gmail.com>
# Creation  : 2019-08-14
# Time-stamp: <Thu 2019-08-15 10:31 juergen>
#
# Copyright (c) 2019 Juergen Hackl <hackl.research@gmail.com>
# =============================================================================
import os

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if f.endswith('.tex'):
        print(f)
        os.system('pdflatex {}'.format(f))

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if not f.endswith('.tex') and not f.endswith('.pdf') and not f.endswith('.py'):
        os.system('rm {}'.format(f))


# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
