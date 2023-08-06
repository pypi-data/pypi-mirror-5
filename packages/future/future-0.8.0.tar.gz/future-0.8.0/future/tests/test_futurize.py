# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import pprint
from subprocess import Popen, PIPE
import os

from future.tests.base import CodeHandler, unittest


class TestFuturizeSimple(CodeHandler):
    """
    This class contains snippets of Python 2 code (invalid Python 3) and
    tests for whether they can be passed to ``futurize`` and immediately
    run under both Python 2 again and Python 3.
    """

    @unittest.expectedFailure
    def test_problematic_string(self):
        """ This string generates a SyntaxError on Python 3 unless it has
        an r prefix.
        """
        before = r"""
        s = 'The folder is "C:\Users"'.
        """
        after = r"""
        s = r'The folder is "C:\Users"'.
        """
        self.convert_check(before, after)

    def test_xrange(self):
        code = '''
        for i in xrange(10):
            pass
        '''
        self.convert_check(code)
    
    @unittest.expectedFailure
    def test_source_coding_utf8(self):
        """
        Tests to ensure that the source coding line is not corrupted or
        removed. It must be left as the first line in the file (including
        before any __future__ imports). Also tests whether the unicode
        characters in this encoding are parsed correctly and left alone.
        """
        code = """
        # -*- coding: utf-8 -*-
        icons = [u"◐", u"◓", u"◑", u"◒"]
        """
        self.unchanged(code)

    def test_exception_syntax(self):
        """
        Test of whether futurize handles the old-style exception syntax
        """
        before = """
        try:
            pass
        except IOError, e:
            val = e.errno
        """
        after = """
        try:
            pass
        except IOError as e:
            val = e.errno
        """
        self.convert_check(before, after)

    def test_super(self):
        """
        This tests whether futurize keeps the old two-argument super() calls the
        same as before. It should, because this still works in Py3.
        """
        code = '''
        class VerboseList(list):
            def append(self, item):
                print('Adding an item')
                super(VerboseList, self).append(item)
        '''
        self.unchanged(code)

    @unittest.expectedFailure
    def test_file(self):
        """
        file() as a synonym for open() is obsolete and invalid on Python 3.
        """
        before = '''
        f = file(__file__)
        data = f.read()
        f.close()
        '''
        after = '''
        f = open(__file__)
        data = f.read()
        f.close()
        '''
        self.convert_check(before, after)

    def test_apply(self):
        before = '''
        def addup(*x):
            return sum(x)
        
        assert apply(addup, (10,20)) == 30
        '''
        after = """
        def addup(*x):
            return sum(x)
        
        assert addup(*(10,20)) == 30
        """
        self.convert_check(before, after, run=True)
    
    @unittest.skip('not implemented yet')
    def test_download_pypi_package_and_test(self, package_name='future'):
        URL = 'http://pypi.python.org/pypi/{}/json'
        
        from future import standard_library
        import requests
        r = requests.get(URL.format(package_name))
        pprint.pprint(r.json())
        
        download_url = r.json()['urls'][0]['url']
        filename = r.json()['urls'][0]['filename']
        # r2 = requests.get(download_url)
        # with open('/tmp/' + filename, 'w') as tarball:
        #     tarball.write(r2.content)

        # Ideally, we'd be able to use code like this:
        # import urllib.request
        # 
        # r = urllib.request.urlopen(URL.format(package_name))
        # pprint.pprint(r.read()) 

    def test_raw_input(self):
        """
        Passes in a string to the waiting input() after futurize
        conversion.

        The code is the first snippet from these docs:
            http://docs.python.org/2/library/2to3.html
        """
        before = """
        def greet(name):
            print "Hello, {0}!".format(name)
        print "What's your name?"
        name = raw_input()
        greet(name)
        """
        desired = """
        def greet(name):
            print("Hello, {0}!".format(name))
        print("What's your name?")
        name = input()
        greet(name)
        """
        self._write_test_script(self.reformat(before))
        self._futurize_test_script()
        output = self._read_test_script()
        self.compare(output, self.headers2 + self.reformat(desired))

        for interpreter in self.interpreters:
            p1 = Popen([interpreter, self.tempdir + 'mytestscript.py'],
                       stdout=PIPE, stdin=PIPE, stderr=PIPE, env=self.env)
            (stdout, stderr) = p1.communicate(b'Ed')
            self.assertEqual(stdout, b"What's your name?\nHello, Ed!\n")

    def test_literal_prefixes_are_not_stripped(self):
        """
        Tests to ensure that the u'' and b'' prefixes on unicode strings and
        byte strings are not removed by the futurize script.  Removing the
        prefixes on Py3.3+ is unnecessary and loses some information -- namely,
        that the strings have explicitly been marked as unicode, rather than
        just the futurize script's guess (perhaps incorrect) that they should
        be unicode.
        """
        code = '''
        s = u'unicode string'
        b = b'byte string'
        '''
        self.unchanged(code)


class TestFuturizeRenamedModules(CodeHandler):
    def test_renamed_modules(self):
        before = """
        import ConfigParser
        import copy_reg
        import cPickle
        import cStringIO

        s = cStringIO.StringIO('blah')
        """
        after = """
        import configparser
        import copyreg
        import pickle
        import io

        s = io.StringIO('blah')
        """
        self.convert_check(before, after)
    
    def test_renamed_copy_reg_module(self):
        """
        Example from docs.python.org/2/library/copy_reg.html
        """
        before = """
        import copy_reg
        import copy
        import cPickle
        class C(object):
            def __init__(self, a):
                self.a = a

        def pickle_c(c):
            print('pickling a C instance...')
            return C, (c.a,)

        copyreg.pickle(C, pickle_c)
        c = C(1)
        d = copy.copy(c)
        p = cPickle.dumps(c)
        """
        after = """
        import copyreg
        import copy
        import pickle
        class C(object):
            def __init__(self, a):
                self.a = a

        def pickle_c(c):
            print('pickling a C instance...')
            return C, (c.a,)

        copyreg.pickle(C, pickle_c)
        c = C(1)
        d = copy.copy(c)
        p = pickle.dumps(c)
        """
        self.convert_check(before, after)

    @unittest.expectedFailure
    def test_Py2_StringIO_module(self):
        """
        TODO: add the Py3 equivalent for this to the docs
        """
        before = """
        import cStringIO
        s = cStringIO.StringIO('my string')
        assert isinstance(s, cStringIO.InputType)
        """
        self.assertTrue(False)


class TestFuturizeStage1(CodeHandler):
    """
    Tests "stage 1": safe optimizations: modernizing Python 2 code so that it
    uses print functions, new-style exception syntax, etc.

    The behaviour should not change and this should introduce no dependency on
    the ``future`` package. It produces more modern Python 2-only code. The
    goal is to reduce the size of the real porting patch-set by performing
    the uncontroversial patches first.
    """

    def test_xrange(self):
        """
        xrange should not be changed by futurize --stage1
        """
        code = '''
        for i in xrange(10):
            pass
        '''
        self.unchanged(code, stages=[1])

    def test_safe_futurize_imports(self):
        """
        The standard library module names should not be changed until stage 2
        """
        before = """
        import ConfigParser
        import HTMLParser
        import collections

        ConfigParser.ConfigParser
        HTMLParser.HTMLParser
        d = collections.OrderedDict()
        """
        self.unchanged(before, stages=[1])

    def test_print(self):
        before = """
        print 'Hello'
        """
        after = """
        print('Hello')
        """
        self.convert_check(before, after, stages=[1])

        before = """
        import sys
        print >> sys.stderr, 'Hello', 'world'
        """
        after = """
        import sys
        print('Hello', 'world', file=sys.stderr)
        """
        self.convert_check(before, after, stages=[1])

    def test_exceptions(self):
        before = """
        try:
            raise AttributeError('blah')
        except AttributeError, e:
            pass
        """
        after = """
        try:
            raise AttributeError('blah')
        except AttributeError as e:
            pass
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_string_exceptions(self):
        """
        2to3 does not convert string exceptions: see
        http://python3porting.com/differences.html.
        """
        before = """
        try:
            raise "old string exception"
        except Exception, e:
            pass
        """
        after = """
        try:
            raise Exception("old string exception")
        except Exception as e:
            pass
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_oldstyle_classes(self):
        """
        We don't convert old-style classes to new-style automatically. Should we?
        """
        before = """
        class Blah:
            pass
        """
        after = """
        class Blah(object):
            pass
        """
        self.convert_check(before, after, stages=[1])

    # TODO: implement this!
    @unittest.expectedFailure
    def test_division(self):
        before = """
        x = 1 / 2
        """
        after = """
        from future.utils import old_div
        x = old_div(1, 2)
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_all(self):
        """
        Standard library module names should not be changed in stage 1
        """
        before = """
        import ConfigParser
        import HTMLParser
        import collections

        print 'Hello'
        try:
            raise AttributeError('blah')
        except AttributeError, e:
            pass
        print 'Number is', 1 / 2
        """
        after = """
        from future.utils import old_div
        import Configparser
        import HTMLParser
        import collections

        print('Hello')
        try:
            raise AttributeError('blah')
        except AttributeError as e:
            pass
        print('Number is', old_div(1, 2))
        """
        self.convert_check(before, after, stages=[1])
        
    def test___future___import_position(self):
        """
        Issue #4: __future__ imports inserted too low in file: SyntaxError
        """
        code = """
        # Comments here
        # and here
        __version__=''' $Id$ '''
        __doc__="A Sequencer class counts things. It aids numbering and formatting lists."
        __all__='Sequencer getSequencer setSequencer'.split()
        #
        # another comment
        #
        
        CONSTANTS = [ 0, 01, 011, 0111, 012, 02, 021, 0211, 02111, 013 ]
        _RN_LETTERS = "IVXLCDM"
        
        def my_func(value):
            pass
        
        ''' Docstring-like comment here '''
        """
        self.convert_check(code)


if __name__ == '__main__':
    unittest.main()
