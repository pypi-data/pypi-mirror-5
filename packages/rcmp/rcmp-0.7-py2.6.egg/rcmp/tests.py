#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Time-stamp: <05-Jul-2013 13:32:43 PDT by rich@noir.com>

# Copyright (c) 2010 - 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
tests for rcmp.
"""

from __future__ import unicode_literals, print_function

__docformat__ = 'restructuredtext en'

import abc
import os
import shutil
import subprocess

import nose
from nose.tools import assert_false, assert_equal, raises

import rcmp

verbose_logging = False
if verbose_logging:
    import logging
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

def isfile(filename):
    assert os.path.isfile(filename), 'missing {}'.format(filename)

rcmp_py = os.path.join('rcmp', '__init__.py')
tests_py = os.path.join('rcmp', 'tests.py')

class testBasics(object):
    nosuch = 'nosuchfileordirectory'

    def __init__(self):
        self.testfilenames = [rcmp_py, tests_py]
        self.itestfiles = [rcmp.Items.find_or_create(f) for f in self.testfilenames]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @raises(rcmp.IndeterminateResult)
    def testEmpty(self):
        rcmp.Comparison(lname=self.testfilenames[0], rname=self.testfilenames[0], comparators=[]).cmp()

    @raises(rcmp.IndeterminateResult)
    def testMissing(self):
        rcmp.Comparison(lname=self.testfilenames[0], rname=self.nosuch, comparators=[]).cmp()

    @raises(rcmp.IndeterminateResult)
    def testEmptyList(self):
        rcmp.ComparisonList([[self.testfilenames[0]], [self.testfilenames[0]]], comparators=[]).cmp()

    def testNoSuchRight(self):
        assert_equal(rcmp.Comparison(lname=self.testfilenames[0], rname=self.nosuch, comparators=[
            rcmp.NoSuchFileComparator(),
            ]).cmp(), rcmp.Different)

    def testNoSuchLeft(self):
        assert_equal(rcmp.Comparison(lname=self.nosuch, rname=self.testfilenames[0], comparators=[
            rcmp.NoSuchFileComparator(),
            ]).cmp(), rcmp.Different)

    def testNoSuchBoth(self):
        assert_equal(rcmp.Comparison(lname=self.nosuch, rname=self.nosuch, comparators=[
            rcmp.NoSuchFileComparator(),
            ]).cmp(), rcmp.Same)

    @raises(rcmp.IndeterminateResult)
    def testNoSuchNeither(self):
        assert_false(rcmp.Comparison(lname=self.testfilenames[0], rname=self.testfilenames[0], comparators=[
            rcmp.NoSuchFileComparator(),
            ]).cmp())

    def testInode(self):
        assert_equal(rcmp.Comparison(lname=self.testfilenames[0], rname=self.testfilenames[0], comparators=[
            rcmp.InodeComparator(),
            ]).cmp(), rcmp.Same)

    def testInodeList(self):
        assert_equal(rcmp.ComparisonList([[self.testfilenames[0]], [self.testfilenames[0]]], comparators=[
            rcmp.InodeComparator(),
            ]).cmp(), rcmp.Same)

    @raises(rcmp.IndeterminateResult)
    def testInodeIndeterminate(self):
        assert_equal(rcmp.Comparison(lname=self.testfilenames[0], rname=self.testfilenames[1], comparators=[
            rcmp.InodeComparator(),
            ]).cmp(), False)

    @raises(rcmp.IndeterminateResult)
    def testInodeIndeterminateList(self):
        assert_equal(rcmp.ComparisonList([[self.testfilenames[0]], [self.testfilenames[1]]], comparators=[
            rcmp.InodeComparator(),
            ]).cmp(), False)

    def testBitwise(self):
        assert_equal(rcmp.Comparison(lname=self.testfilenames[0], rname=self.testfilenames[0], comparators=[
            rcmp.BitwiseComparator(),
            ]).cmp(), rcmp.Same)

    def testBitwiseList(self):
        assert_equal(rcmp.ComparisonList([[self.testfilenames[0]], [self.testfilenames[0]]], comparators=[
            rcmp.BitwiseComparator(),
            ]).cmp(), rcmp.Same)

    @raises(rcmp.IndeterminateResult)
    def testBitwiseIndeterminate(self):
        assert_equal(rcmp.Comparison(lname=self.testfilenames[0], rname=self.testfilenames[1], comparators=[
            rcmp.BitwiseComparator(),
            ]).cmp(), False)

    @raises(rcmp.IndeterminateResult)
    def testBitwiseIndeterminateList(self):
        assert_equal(rcmp.ComparisonList([[self.testfilenames[0]], [self.testfilenames[1]]], comparators=[
            rcmp.BitwiseComparator(),
            ]).cmp(), False)

    def testElf(self):
        lname = os.path.join('testfiles', 'left', 'main.o')
        rname = os.path.join('testfiles', 'right', 'main.o')
        isfile(lname)
        isfile(rname)
        assert_equal(rcmp.Comparison(lname=lname,
                                     rname=rname,
                                     comparators=[
        				rcmp.ElfComparator(),
                                     ]).cmp(), rcmp.Same)


class testDirDirect(object):
    emptydirname = 'emptydir'
    dirnotemptybase = 'notempty'
    foilername = 'foiler'

    def setUp(self):
        os.makedirs(self.emptydirname)
        os.makedirs(os.path.join(self.dirnotemptybase, self.foilername))

    def tearDown(self):
        shutil.rmtree(self.emptydirname)
        shutil.rmtree(self.dirnotemptybase)

    def testDirDirect(self):
        itestdir = rcmp.Items.find_or_create(self.emptydirname)
        itestdir2 = rcmp.Items.find_or_create(self.dirnotemptybase)

        assert_equal(rcmp.Comparison(litem=itestdir, ritem=itestdir, comparators=[
            rcmp.DirComparator([]),
            ]).cmp(), rcmp.Same)

        assert_equal(rcmp.ComparisonList([[self.emptydirname], [self.emptydirname]], comparators=[
            rcmp.DirComparator([]),
            ]).cmp(), rcmp.Same)

        assert_equal(rcmp.Comparison(litem=itestdir, ritem=itestdir, comparators=[
            rcmp.DirComparator(),
            ]).cmp(), rcmp.Same)

        assert_equal(rcmp.ComparisonList([[self.emptydirname], [self.emptydirname]], comparators=[
            rcmp.DirComparator(),
            ]).cmp(), rcmp.Same)

        assert_equal(rcmp.Comparison(litem=itestdir, ritem=itestdir2, comparators=[
            rcmp.DirComparator(),
            ]).cmp(), rcmp.Different)

        assert_equal(rcmp.ComparisonList([[self.emptydirname], [self.dirnotemptybase]], comparators=[
            rcmp.DirComparator(),
            ]).cmp(), rcmp.Different)

        assert_equal(rcmp.ComparisonList([[self.emptydirname], [self.dirnotemptybase]], comparators=[
            rcmp.DirComparator(),
            ], ignores=['*' + self.foilername]).cmp(), rcmp.Same)

    def testReal(self):
        itestdir = rcmp.Items.find_or_create(self.emptydirname)

        r = rcmp.Comparison(litem=itestdir, ritem=itestdir)
        assert_equal(r.cmp(), rcmp.Same)


class testTreeBase(object):
    def setUp(self):
        dirs = ['red', 'blue']

        for dir in dirs:
            try:
                shutil.rmtree(dir)
            except:
                pass

        dirs2 = [os.path.join(p, q) for p in ['red', 'blue'] for q in ['ham', 'eggs', 'spam', 'sam',
                                                                       'I', 'am', 'do', 'not',
                                                                       'like']]

        for dir in dirs + dirs2:
            os.makedirs(dir)

            for filename in ['foo', 'bar', 'baz', 'bim',
                             'george', 'fred', 'carol', 'ted',
                             'alice']:
                with open(os.path.join(dir, filename), 'wb') as f:
                    print(filename, file=f)

    def tearDown(self):
        for dir in ['red', 'blue']:
            try:
                shutil.rmtree(dir)
            except:
                pass

class testTree(testTreeBase):
    def testCase1(self):
        assert_equal(rcmp.Comparison(lname='red', rname='blue').cmp(), rcmp.Same)

    def testCaseDefaultLogger(self):
        assert_equal(rcmp.Comparison(lname='red', rname='blue').cmp(), rcmp.Same)

    def testFallThrough(self):
        r = rcmp.Comparison(lname=os.path.join('red', 'ham', 'foo'), rname=os.path.join('blue', 'eggs', 'bar'))
        assert_equal(r.cmp(), rcmp.Different)

class testTreeAux(testTreeBase):
    def setUp(self):
        testTreeBase.setUp(self)

        for dir in ['red', 'blue']:
            filename = os.path.abspath(os.path.join(dir, 'ham', 'foo.pyc'))
            with open(filename, 'wb') as f:
                print(filename, file=f)

    def testBuried(self):
        assert_equal(rcmp.Comparison(lname=os.path.join('red', 'ham', 'foo.pyc'),
                                     rname=os.path.join('blue', 'ham', 'foo.pyc'),
                                     comparators=[
            				rcmp.BuriedPathComparator(),
                                        ]).cmp(), rcmp.Same)

    def testIgnore(self):
        assert_equal(rcmp.Comparison(lname='red', rname='blue', ignores=['*.pyc']).cmp(), rcmp.Same)


class testSymlinks(testTreeBase):
    def setUp(self):
        testTreeBase.setUp(self)

        self.red_sausage = os.path.join('red', 'sausage')
        self.red_bacon = os.path.join('red', 'bacon')
        self.red_bird = os.path.join('red', 'bird')

        self.blue_sausage = os.path.join('blue', 'sausage')
        self.blue_bacon = os.path.join('blue', 'bacon')
        self.blue_bird = os.path.join('blue', 'bird')

        os.symlink('foo', self.red_bird)
        os.symlink('nonexistent', self.red_sausage)
        os.symlink('ham', self.red_bacon)

        os.symlink('foo', self.blue_bird)
        os.symlink('nonexistent', self.blue_sausage)
        os.symlink('ham', self.blue_bacon)

    def testBird(self):
        assert_equal(rcmp.Comparison(lname=self.red_bird, rname=self.blue_bird).cmp(), rcmp.Same)

    def testBacon(self):
        assert_equal(rcmp.Comparison(lname=self.red_bacon, rname=self.blue_bacon).cmp(), rcmp.Same)

    def testSausage(self):
        assert_equal(rcmp.Comparison(lname=self.red_sausage, rname=self.blue_sausage).cmp(), rcmp.Same)

    def testDir(self):
        assert_equal(rcmp.Comparison(lname='red', rname='blue').cmp(), rcmp.Same)


class testCommonSuffix(object):
    def testSimple(self):
        assert_equal(rcmp._findCommonSuffix('a/b/c', 'a/b/c'), ('', '', 'a/b/c'))
        assert_equal(rcmp._findCommonSuffix('a/b/c', 'd/e/f'), ('a/b/c', 'd/e/f', ''))
        assert_equal(rcmp._findCommonSuffix('b/a', 'c/a'), ('b', 'c', 'a'))
        assert_equal(rcmp._findCommonSuffix('a/b/c', 'd/e/c'), ('a/b', 'd/e', 'c'))
        assert_equal(rcmp._findCommonSuffix('a/b/c/d', 'e/f/c/d'), ('a/b', 'e/f', 'c/d'))
        assert_equal(rcmp._findCommonSuffix('a/b/c/d', 'e/f/g/d'), ('a/b/c', 'e/f/g', 'd'))
        assert_equal(rcmp._findCommonSuffix('a/b/c/d', 'e/b/c/d'), ('a', 'e', 'b/c/d'))

class testAr(object):
    empty = 'empty.a'
    first = 'first.a'
    second = 'second.a'
    third = 'third.a'
    left = os.path.join('testfiles', 'left', 'archive.a')
    isfile(left)
    right = os.path.join('testfiles', 'right', 'archive.a')
    isfile(right)

    def setUp(self):
        with open(self.empty, 'wb') as f:
            f.write('!<arch>\n')

        subprocess.check_call(['ar', 'cr', self.first, rcmp_py])
        subprocess.check_call(['ar', 'cr', self.second, rcmp_py])
        subprocess.check_call(['ar', 'cr', self.third, rcmp_py, tests_py])

    def tearDown(self):
        for i in [self.empty, self.first, self.second, self.third]:
            os.remove(i)

    def testEmpty(self):
        assert_equal(rcmp.Comparison(lname=self.empty, rname=self.empty, comparators=[
            rcmp.ArMemberMetadataComparator(),
            rcmp.ArComparator(),
            ]).cmp(), rcmp.Same)

    def testIdentical(self):
        r = rcmp.Comparison(lname=self.first, rname=self.first, comparators=[
            rcmp.ArMemberMetadataComparator(),
            rcmp.ArComparator(),
            rcmp.BitwiseComparator(),
            ])
        assert_equal(r.cmp(), rcmp.Same)

    def testTwo(self):
        assert_equal(rcmp.Comparison(lname=self.first, rname=self.second, comparators=[
            rcmp.ArMemberMetadataComparator(),
            rcmp.ArComparator(),
            rcmp.BitwiseComparator(),
            ]).cmp(), rcmp.Same)

    def testDifferent(self):
        assert_equal(rcmp.Comparison(lname=self.first, rname=self.third, comparators=[
            rcmp.ArMemberMetadataComparator(),
            rcmp.ArComparator(),
            ]).cmp(), rcmp.Different)

    def testOtherDifferent(self):
        assert_equal(rcmp.Comparison(lname=self.third, rname=self.first, comparators=[
            rcmp.ArMemberMetadataComparator(),
            rcmp.ArComparator(),
            ]).cmp(), rcmp.Different)

    def testArElf(self):
        r = rcmp.Comparison(lname=self.left, rname=self.right, comparators=[
            rcmp.ArMemberMetadataComparator(),
            rcmp.ArComparator(),
            rcmp.ElfComparator(),
            ])
        assert_equal(r.cmp(), rcmp.Same)

class SimpleAbstract(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def filenames(self):
        return None

    @abc.abstractproperty
    def comparators(self):
        return []

    sides = ['left', 'right']

    def __init__(self):
        (self.lefts, self.rights) = [[os.path.join('testfiles', side, filename) for filename in self.filenames] for side in self.sides]
        for f in self.lefts + self.rights:
            isfile(f)

    def testIdentical(self):
        for left in self.lefts:
            r = rcmp.Comparison(lname=left, rname=left, comparators=self.comparators)
            assert_equal(r.cmp(), rcmp.Same)

    def testOne(self):
        for left, right in zip(self.lefts, self.rights):
            r = rcmp.Comparison(lname=left, rname=right, comparators=self.comparators)
            assert_equal(r.cmp(), rcmp.Same)

    def testReal(self):
        for left, right in zip(self.lefts, self.rights):
            r = rcmp.Comparison(lname=left, rname=right)
            assert_equal(r.cmp(), rcmp.Same)

class testEmpty(SimpleAbstract):
    filenames = ['empty']

    comparators = [
        rcmp.EmptyFileComparator(),
    ]

class testAr2(SimpleAbstract):
    filenames = ['archive.a']

    comparators = [
        rcmp.BitwiseComparator(),
        rcmp.ArMemberMetadataComparator(),
        rcmp.ArComparator(),
    ]

    def setUp(self):
        for side in ['left', 'right']:
            fname = os.path.join('testfiles', side, 'stumper')

            try:
                os.remove(fname)
            except:
                pass

            with open(fname, 'wb'):
                pass
            os.chmod(fname, 0)

    def tearDown(self):
        for side in ['left', 'right']:
            try:
                os.remove(os.path.join('testfiles', side, 'stumper'))

            except OSError, val:
                if val is 2:
                    pass
                else:
                    raise

class testAM(SimpleAbstract):
    filenames = ['Makefile']
    comparators = [rcmp.AMComparator()]

class testConfigLog(SimpleAbstract):
    # don't know what these were.  :(.
    not_filenames = ['2config.log', 'db-config.log', '3config.log' ]
    filenames = ['config.log', 'config.status' ]
    comparators = [rcmp.ConfigLogComparator()]

# FIXME: need some kernel conf files.
# class testKernelConf(SimpleAbstract):
#     filenames = ['auto.conf', 'autoconf.h']
#     comparators = [rcmp.KernelConfComparator()]

class testGzip(SimpleAbstract):
    filenames = ['Makefile.in.gz', 'yo.gz.gz.gz']
    comparators = [rcmp.GzipComparator(), rcmp.BitwiseComparator()]

class testZip(SimpleAbstract):
    #filenames = ['jarfile.jar', 'tst_unzip_file.zip', 'third.zip']
    filenames = ['zipfile.zip']
    comparators = [
        rcmp.ZipMemberMetadataComparator(),
        rcmp.ZipComparator(),
        rcmp.BitwiseComparator(),
        ]

    testdir = 'testfiles'
    nullfilename = 'nullfile.zip'
    emptyfilename = 'emptyfile.zip'
    fnames = []

    def __init__(self):
        self.fnames = []
        SimpleAbstract.__init__(self)

    def setUp(self):
        for fname in [os.path.join(self.testdir, side, self.nullfilename) for side in ['left', 'right']]:
            self.fnames.append(fname)
            with open(fname, 'wb'):
                pass

        for fname in [os.path.join(self.testdir, side, self.emptyfilename) for side in ['left', 'right']]:
            self.fnames.append(fname)
            with rcmp.openzip(fname, 'w') as f:
                pass

    def tearDown(self):
        for fname in self.fnames:
            os.remove(fname)

# FIXME: need some test files
# class testDateBlot(SimpleAbstract):
#     filenames = ['icu-config', 'acinclude.m4', 'compile.h']
#     comparators = [rcmp.DateBlotBitwiseComparator()]

class testCpio(SimpleAbstract):
    filenames = ['cpiofile.cpio']
    comparators = [
        rcmp.CpioMemberMetadataComparator(),
        rcmp.CpioComparator(),
        rcmp.BitwiseComparator(),
        ]

class testTar(SimpleAbstract):
    filenames = ['tarfile.tar']
    comparators = [
        rcmp.TarMemberMetadataComparator(),
        rcmp.TarComparator(),
        rcmp.BitwiseComparator(),
        ]

# def testNew():
#     assert_equal(rcmp.Comparison(lname='testfiles/left/libpulse_0.9.22-6_opal.ipk',
#                                  rname='testfiles/right/libpulse_0.9.22-6_opal.ipk',
#                                  ignores=['*/temp']).cmp(),
#                  rcmp.Same)

if __name__ == '__main__':
    nose.main()
