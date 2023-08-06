"""
Python 3 reorganized the standard library (PEP 3108). This module exposes
several standard library modules to Python 2 under their new Python 3
names.

It is designed to be used as follows:

    from future import standard_library_renames

And then, for example:

    import builtins
    import configparser
    import copyreg
    import queue
    import socketserver
    import tkinter

We don't currently support these, but would like to:

    import http.cookies
    import http.server
    import urllib.parse
    import xmlrpc.client

This module only supports Python 2.7 and Python 3.1+.
"""

from __future__ import absolute_import, print_function

import inspect
import importlib
import sys
import warnings
import logging
import imp

from . import six

mapping = {thing.mod: thing.name for thing in six._moved_attributes \
           if isinstance(thing, six.MovedModule)}
import pprint
pprint.pprint(mapping)

mapping = {'ConfigParser': 'configparser',
           'Queue': 'queue',
           'SocketServer': 'socketserver',
           'Tkinter': 'tkinter',
           '_winreg': 'winreg',
           '__builtin__': 'builtins',
           'copy_reg': 'copyreg',
           'repr': 'reprlib',
          }
pprint.pprint(mapping)


# class ImportBlocker(object):
#     def __init__(self, *args):
#         self.module_names = args
#     
#     def find_module(self, fullname, path=None):
#         if fullname in self.module_names:
#             return self
#         return None
#     
#     def load_module(self, name):
#         raise ImportError("%s is blocked and cannot be imported" % name)
# 
# print(sys.meta_path)
# sys.meta_path = [ImportBlocker('ConfigParser')]

	

class WarnOnImport(object):
    def __init__(self, *args):
        self.module_names = args
 
    def find_module(self, fullname, path=None):
        if fullname in self.module_names:
            self.path = path
            return self
        return None
 
    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        module_info = imp.find_module(name, self.path)
        module = imp.load_module(name, *module_info)
        sys.modules[name] = module
 
        logging.warning("Imported deprecated module %s", name)
        return module


class RenameImport(object):
    def __init__(self, old_to_new):
        '''
        Pass in a dictionary-like object mapping from old names to new
        names. E.g. {'ConfigParser': 'configparser', 'cPickle': 'pickle'}
        '''
        self.old_to_new = old_to_new
        both = set(old_to_new.keys()) & set(old_to_new.values())
        print(both)
        assert len(both) == 0
        self.new_to_old = {new: old for (old, new) in old_to_new.items()}
 
    def find_module(self, fullname, path=None):
        if fullname in set(self.old_to_new) | set(self.new_to_old):
            self.path = path
            return self
        return None
 
    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        if name in self.new_to_old:
            # New name
            oldname = self.new_to_old[name]
            module_info = imp.find_module(oldname, self.path)
            module = imp.load_module(oldname, *module_info)
        elif name in self.old_to_new:
            # Old name. Import with warning.
            module_info = imp.find_module(name, self.path)
            module = imp.load_module(name, *module_info)
            logging.warning("Imported deprecated module %s", name)
        else: 
            # Something else
            module_info = imp.find_module(name, self.path)
            module = imp.load_module(name, *module_info)
        sys.modules[name] = module
        return module
 

#sys.meta_path = [WarnOnImport('getopt', 'optparse')]
sys.meta_path = [RenameImport(mapping)]

if not six.PY3 and False:
    for oldname, newname in mapping.items():
        print('Importing module ' + oldname)
        module = importlib.import_module(oldname, package=None)
        #try:
        #except ImportError as e:
        #     raise e
        #     # Expected to fail (on non-Windows ...)
        #     if oldname != '_winreg':
        #         warnings.warn('Could not import module ' + oldname)
        # else:
        #     sys.modules[newname] = module
        sys.modules[oldname] = None
        # module.__name__ = newname   # has no effect?!

    caller = inspect.currentframe().f_back
    # caller.f_globals[newname] = oldname

# print(len(sys.modules))
