"""
For the ``future`` package.

Adds this import line:

    from future import *

after any other imports (in an initial block of them).
"""

from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import touch_import
from lib2to3.pygram import python_symbols as syms

       
class FixFutureBuiltins(BaseFix):

    def match(self, node):
        if node.type == syms.file_input:
            return True
        return False
    
    def transform(self, node, results):
        touch_import(u'future', u'*', node)

