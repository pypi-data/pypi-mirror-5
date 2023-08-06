"""
Python 3 reorganized the standard library (PEP 3108). This module exposes
several standard library modules to Python 2 under their new Python 3
names.

It is designed to be used as follows::

    from future import standard_library

And then these imports work::

    import builtins
    import configparser
    import copyreg
    import queue
    import reprlib
    import socketserver
    import winreg    # on Windows only
    import test.support
    import html, html.parser, html.entites
    import http, http.client, http.server, http.cookies, http.cookiejar
    import _thread
    import _dummythread
    import html, html.parser, html.entites
    import http, http.client, http.server, http.cookies, http.cookiejar
    import _markupbase
    

The modules are still available under their old names on Python 2.

This is a cleaner alternative to this idiom (see
http://docs.pythonsprints.com/python3_porting/py-porting.html)::

    try:
        import queue
    except ImportError:
        import Queue as queue


We don't currently support these, but would like to::

    import pickle     # should (optionally) bring in cPickle on Python 2
    import dbm
    import dbm.dumb
    import dbm.gnu
    import xmlrpc.client
    import collections.abc  # on Py33
    import urllib.request
    import urllib.parse
    import urllib.error
    import urllib.robotparser
    import tkinter

These renames are already supported on Python 2.7 without any additional work
from us:
    reload() -> imp.reload()
    reduce() -> functools.reduce()
    StringIO.StringIO -> io.StringIO
    Bytes.BytesIO -> io.BytesIO

Old things that can perhaps be fixed for people by futurize.py:
  string.uppercase -> string.ascii_uppercase   # works on either Py2.7 or Py3+
  sys.maxint -> sys.maxsize

Other renames/moves we handle:
  itertools.ifilterfalse -> itertools.filterfalse
  intern(s) -> sys.intern(s)

TODO: Check out these:
  unittest2 -> unittest?
  buffer -> memoryview?

This module only supports Python 2.7 and Python 3.1+.
"""

from __future__ import absolute_import, print_function

import sys
import logging
import imp

from . import six

# The modules that are defined under the same names on Py3 but with
# different contents in a significant way (e.g. submodules) are:
#   pickle (fast one)
#   dbm
#   urllib

# These ones are new (i.e. no problem)
#   http
#   html
#   tkinter
#   xmlrpc

# These modules need names from elsewhere being added to them:
#   subprocess: should provide getoutput and other fns from commands
#               module but these fns are missing: getstatus, mk2arg,
#               mkarg

# Old to new
# etc: see lib2to3/fixes/fix_imports.py
RENAMES = {
           # 'cStringIO': 'io',  # there's a new io module in Python 2.6
                                 # that provides StringIO and BytesIO
           # 'StringIO': 'io',   # ditto
           # 'cPickle': 'pickle',
           '__builtin__': 'builtins',
           'copy_reg': 'copyreg',
           'Queue': 'queue',
           'SocketServer': 'socketserver',
           'ConfigParser': 'configparser',
           'repr': 'reprlib',
           # 'FileDialog': 'tkinter.filedialog',
           # 'tkFileDialog': 'tkinter.filedialog',
           # 'SimpleDialog': 'tkinter.simpledialog',
           # 'tkSimpleDialog': 'tkinter.simpledialog',
           # 'tkColorChooser': 'tkinter.colorchooser',
           # 'tkCommonDialog': 'tkinter.commondialog',
           # 'Dialog': 'tkinter.dialog',
           # 'Tkdnd': 'tkinter.dnd',
           # 'tkFont': 'tkinter.font',
           # 'tkMessageBox': 'tkinter.messagebox',
           # 'ScrolledText': 'tkinter.scrolledtext',
           # 'Tkconstants': 'tkinter.constants',
           # 'Tix': 'tkinter.tix',
           # 'ttk': 'tkinter.ttk',
           # 'Tkinter': 'tkinter',
           '_winreg': 'winreg',
           'thread': '_thread',
           'dummy_thread': '_dummy_thread',
           # 'anydbm': 'dbm',   # causes infinite import loop 
           # 'whichdb': 'dbm',  # causes infinite import loop 
           # anydbm and whichdb are handled by fix_imports2
           # 'dbhash': 'dbm.bsd',
           # 'dumbdbm': 'dbm.dumb',
           # 'dbm': 'dbm.ndbm',
           # 'gdbm': 'dbm.gnu',
           # 'xmlrpclib': 'xmlrpc.client',
           # 'DocXMLRPCServer': 'xmlrpc.server',
           # 'SimpleXMLRPCServer': 'xmlrpc.server',
           # 'httplib': 'http.client',
           # 'htmlentitydefs' : 'html.entities',
           # 'HTMLParser' : 'html.parser',
           # 'Cookie': 'http.cookies',
           # 'cookielib': 'http.cookiejar',
           # 'BaseHTTPServer': 'http.server',
           # 'SimpleHTTPServer': 'http.server',
           # 'CGIHTTPServer': 'http.server',
           'future.backports.test': 'test',  # primarily for renaming test_support to support
           # 'commands': 'subprocess',
           # 'urlparse' : 'urllib.parse',
           # 'robotparser' : 'urllib.robotparser',
           # 'abc': 'collections.abc',   # for Py33
           'future.backports.html': 'html',
           'future.backports.http': 'http',
           # 'future.backports.urllib': 'newurllib',
           'future.backports._markupbase': '_markupbase',
          }

REPLACED_MODULES = {'test', 'urllib', 'pickle'}  # add dbm when we support it
# These are entirely new to Python 2.7, so they cause no potential clashes
#   xmlrpc, tkinter, http, html


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
        # print(both)
        assert len(both) == 0, \
               'Ambiguity in renaming (handler not implemented'
        self.new_to_old = {new: old for (old, new) in old_to_new.items()}
 
    def find_module(self, fullname, path=None):
        # Handles hierarchical importing: package.module.module2
        new_base_names = {s.split('.')[0] for s in self.new_to_old}
        if fullname in set(self.old_to_new) | new_base_names:
            return self
        return None
 
    def load_module(self, name):
        path = None
        if name in sys.modules:
            return sys.modules[name]
        elif name in self.new_to_old:
            # New name. Look up the corresponding old (Py2) name:
            name = self.new_to_old[name]
        module = self._find_and_load_module(name)
        sys.modules[name] = module
        return module
 
    def _find_and_load_module(self, name, path=None):
        """
        Finds and loads it. But if there's a . in the name, handles it
        properly.
        """
        bits = name.split('.')
        while len(bits) > 1:
            # Treat the first bit as a package
            packagename = bits.pop(0)
            package = self._find_and_load_module(packagename, path)
            path = package.__path__
        name = bits[0]
        module_info = imp.find_module(name, path)
        return imp.load_module(name, *module_info)

# (New module name, new object name, old module name, old object name)
MOVES = [('collections', 'UserList', 'UserList', 'UserList'),
         ('collections', 'UserDict', 'UserDict', 'UserDict'),
         ('collections', 'UserString','UserString', 'UserString'),
         ('itertools', 'filterfalse','itertools', 'ifilterfalse'),
         ('sys', 'intern','__builtin__', 'intern'),
         # urllib._urlopener	urllib.request
         # urllib.ContentTooShortError	urllib.error
         # urllib.FancyURLOpener	urllib.request
         # urllib.pathname2url	urllib.request
         # urllib.quote	urllib.parse
         # urllib.quote_plus	urllib.parse
         # urllib.splitattr	urllib.parse
         # urllib.splithost	urllib.parse
         # urllib.splitnport	urllib.parse
         # urllib.splitpasswd	urllib.parse
         # urllib.splitport	urllib.parse
         # urllib.splitquery	urllib.parse
         # urllib.splittag	urllib.parse
         # urllib.splittype	urllib.parse
         # urllib.splituser	urllib.parse
         # urllib.splitvalue	urllib.parse
         # urllib.unquote	urllib.parse
         # urllib.unquote_plus	urllib.parse
         # urllib.urlcleanup	urllib.request
         # urllib.urlencode	urllib.parse
         # urllib.urlopen	urllib.request
         # urllib.URLOpener	urllib.request
         # urllib.urlretrieve	urllib.request
         # urllib2.AbstractBasicAuthHandler	urllib.request
         # urllib2.AbstractDigestAuthHandler	urllib.request
         # urllib2.BaseHandler	urllib.request
         # urllib2.build_opener	urllib.request
         # urllib2.CacheFTPHandler	urllib.request
         # urllib2.FileHandler	urllib.request
         # urllib2.FTPHandler	urllib.request
         # urllib2.HTTPBasicAuthHandler	urllib.request
         # urllib2.HTTPCookieProcessor	urllib.request
         # urllib2.HTTPDefaultErrorHandler	urllib.request
         # urllib2.HTTPDigestAuthHandler	urllib.request
         # urllib2.HTTPError	urllib.request
         # urllib2.HTTPHandler	urllib.request
         # urllib2.HTTPPasswordMgr	urllib.request
         # urllib2.HTTPPasswordMgrWithDefaultRealm	urllib.request
         # urllib2.HTTPRedirectHandler	urllib.request
         # urllib2.HTTPSHandler	urllib.request
         # urllib2.install_opener	urllib.request
         # urllib2.OpenerDirector	urllib.request
         # urllib2.ProxyBasicAuthHandler	urllib.request
         # urllib2.ProxyDigestAuthHandler	urllib.request
         # urllib2.ProxyHandler	urllib.request
         # urllib2.Request	urllib.request
         # urllib2.UnknownHandler	urllib.request
         # urllib2.URLError	urllib.request
         # urllib2.urlopen	urllib.request
         # urlparse.parse_qs	urllib.parse
         # urlparse.parse_qsl	urllib.parse
         # urlparse.urldefrag	urllib.parse
         # urlparse.urljoin	urllib.parse
         # urlparse.urlparse	urllib.parse
         # urlparse.urlsplit	urllib.parse
         # urlparse.urlunparse	urllib.parse
         # urlparse.urlunsplit	urllib.parse
        ]

if not six.PY3:
    for (newmodname, newobjname, oldmodname, oldobjname) in MOVES:
        newmod = __import__(newmodname)
        oldmod = __import__(oldmodname)
        obj = getattr(oldmod, oldobjname)
        setattr(newmod, newobjname, obj)

    sys.meta_path = [RenameImport(RENAMES)]

