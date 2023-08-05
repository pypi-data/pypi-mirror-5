# -*- coding: UTF-8 -*-
## Copyright 2012-2013 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

import os,sys
import time
import fnmatch

#~ def codefiles(pattern='.*', flags=0):
def codefiles(pattern='*'):
    """
    Yield a list of the source files corresponding to the currently 
    imported modules which match the given pattern
    """
    #~ exp = re.compile(pattern, flags)
    
    for name,mod in sys.modules.items():
        if fnmatch.fnmatch(name, pattern):
        #~ if exp.match(name):
            filename = getattr(mod, "__file__", None)
            if filename is not None:
                if filename.endswith(".pyc") or filename.endswith(".pyo"):
                    filename = filename[:-1]
                if filename.endswith("$py.class"):
                    filename = filename[:-9] + ".py"
                if os.path.exists(filename): # File might be in an egg, so there's no source available
                    yield name,filename
            
def codetime(*args,**kw):
    """
    Return the modification time of the youngest source code in memory.
    Used by :mod:`lino.ui.extjs3.ext_ui` to avoid generating lino.js files if not necessary.
    Inspired by the code_changed() function in `django.utils.autoreload`.
    """
    code_mtime = None
    pivot = None
    for name,filename in codefiles(*args,**kw):
        stat = os.stat(filename)
        mtime = stat.st_mtime
        if code_mtime is None or code_mtime < mtime:
            #~ print 20130204, filename, time.ctime(mtime) 
            code_mtime = mtime
            pivot = filename
    #~ print '20130204 codetime:', time.ctime(code_mtime), pivot
    return code_mtime
    

def is_start_of_docstring(line):
    for delim in '"""',"'''":
        if line.startswith(delim) or line.startswith('u'+delim) or line.startswith('r'+delim) or line.startswith('ru'+delim):
            return delim
            
class SourceFile(object):
    """
    Counts the number of code lines in a given Python source file.
    """
    def __init__(self,modulename,filename):
        self.modulename = modulename
        self.filename = filename
        self.analyze()
        
    def analyze(self):
        self.count_code, self.count_total, self.count_blank, self.count_doc = 0, 0, 0, 0
        self.count_comment = 0
        #~ count_code, count_total, count_blank, count_doc = 0, 0, 0, 0
        skip_until = None
        for line in open(self.filename).readlines():
            self.count_total += 1
            line = line.strip()
            if not line:
                self.count_blank += 1
            else:
                if line.startswith('#'):
                    self.count_comment += 1
                    continue
                if skip_until is None:
                    skip_until = is_start_of_docstring(line)
                    if skip_until is not None:
                        self.count_doc += 1
                        #~ skip_until = '"""'
                        continue
                    #~ if line.startswith('"""') or line.startswith('u"""'):
                        #~ count_doc += 1
                        #~ skip_until = '"""'
                        #~ continue
                    #~ if line.startswith("'''") or line.startswith("u'''"):
                        #~ count_doc += 1
                        #~ skip_until = "'''"
                        #~ continue
                    self.count_code += 1
                else:
                    self.count_doc += 1
                    #~ if line.startswith(skip_until):
                    if skip_until in line:
                        skip_until = None

        #~ self.count_code, count_total, count_blank, count_doc
        

from lino.utils import rstgen

def analyze_rst(*packages):

    fields = 'count_code count_doc count_comment count_total'.split()
    headers = ["name"] + fields
    rows = []

    total_sums = [0] * len(fields)
    for package in packages:
        sums = [0] * len(fields)
        for name,filename in codefiles(package+'*'):
            sf = SourceFile(name,filename)
            for i,k in enumerate(fields):
                sums[i] += getattr(sf,k)
        rows.append([package]+[str(n) for n in sums])
        for i,k in enumerate(fields):
            total_sums[i] += sums[i]
    rows.append(['total']+[str(n) for n in total_sums])
    return rstgen.table(headers,rows)

