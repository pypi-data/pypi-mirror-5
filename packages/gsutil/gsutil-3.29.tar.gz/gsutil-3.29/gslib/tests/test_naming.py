# Copyright 2010 Google Inc. All Rights Reserved.
# -*- coding: utf-8 -*-
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""Tests for gsutil naming logic.
The test code in this file runs against an in-memory storage service mock,
so runs very quickly. This is valuable for testing changes that impact the
naming rules, since those rules are complex and it's useful to be able to
make small incremental changes and rerun the tests frequently. Additional
end-to-end tests (which send traffic to the production Google Cloud Storage
service) are available via the gsutil test command.
"""

import gzip
import os
import StringIO

import boto
from boto.exception import StorageResponseError
from boto import storage_uri

from gslib.commands import cp
from gslib.exception import CommandException
import gslib.tests.testcase as testcase
from gslib.tests.util import ObjectToURI as suri


class GsutilNamingTests(testcase.GsUtilUnitTestCase):
  """gsutil command method test suite"""

  def testGetPathBeforeFinalDir(self):
    """Tests _GetPathBeforeFinalDir() (unit test)"""
    self.assertEqual('gs://',
                     cp._GetPathBeforeFinalDir(storage_uri('gs://bucket/')))
    self.assertEqual('gs://bucket',
                     cp._GetPathBeforeFinalDir(storage_uri('gs://bucket/dir/')))
    self.assertEqual('gs://bucket',
                     cp._GetPathBeforeFinalDir(storage_uri('gs://bucket/dir')))
    self.assertEqual('gs://bucket/dir',
                     cp._GetPathBeforeFinalDir(
                         storage_uri('gs://bucket/dir/obj')))
    src_dir = self.CreateTempDir()
    subdir = os.path.join(src_dir, 'subdir')
    os.mkdir(subdir)
    self.assertEqual(suri(src_dir),
                     cp._GetPathBeforeFinalDir(storage_uri(suri(subdir))))

  def testCopyingTopLevelFileToBucket(self):
    """Tests copying one top-level file to a bucket"""
    src_file = self.CreateTempFile(file_name='f0')
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', [src_file, suri(dst_bucket_uri)])
    actual = list(self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    self.assertEqual(1, len(actual))
    self.assertEqual('f0', actual[0].object_name)

  def testCopyingMultipleFilesToBucket(self):
    """Tests copying multiple files to a bucket"""
    src_file0 = self.CreateTempFile(file_name='f0')
    src_file1 = self.CreateTempFile(file_name='f1')
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', [src_file0, src_file1, suri(dst_bucket_uri)])
    actual = list(self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    self.assertEqual(2, len(actual))
    self.assertEqual('f0', actual[0].object_name)
    self.assertEqual('f1', actual[1].object_name)

  def testCopyingAbsolutePathDirToBucket(self):
    """Tests recursively copying absolute path directory to a bucket"""
    dst_bucket_uri = self.CreateBucket()
    src_dir_root = self.CreateTempDir(test_files=[
        'f0', 'f1', 'f2.txt', ('dir0', 'dir1', 'nested')])
    self.RunCommand('cp', ['-R', src_dir_root, suri(dst_bucket_uri)])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    src_tmpdir = os.path.split(src_dir_root)[1]
    expected = set([
        suri(dst_bucket_uri, src_tmpdir, 'f0'),
        suri(dst_bucket_uri, src_tmpdir, 'f1'),
        suri(dst_bucket_uri, src_tmpdir, 'f2.txt'),
        suri(dst_bucket_uri, src_tmpdir, 'dir0', 'dir1', 'nested')])
    self.assertEqual(expected, actual)

  def testCopyingRelativePathDirToBucket(self):
    """Tests recursively copying relative directory to a bucket"""
    dst_bucket_uri = self.CreateBucket()
    src_dir = self.CreateTempDir(test_files=[('dir0', 'f1')])
    self.RunCommand('cp', ['-R', 'dir0', suri(dst_bucket_uri)], cwd=src_dir)
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'dir0', 'f1')])
    self.assertEqual(expected, actual)

  def testCopyingRelPathSubDirToBucketSubdirWithDollarFolderObj(self):
    """Tests recursively copying relative sub-directory to bucket subdir
    signified by a $folder$ object"""
    # Create a $folder$ object to simulate a folder created by GCS manager (or
    # various other tools), which gsutil understands to mean there is a folder
    # into which the object is being copied.
    dst_bucket_uri = self.CreateBucket()
    self.CreateObject(bucket_uri=dst_bucket_uri, object_name='abc_$folder$',
                      contents='')
    src_dir = self.CreateTempDir(test_files=[('dir0', 'dir1', 'f1')])
    self.RunCommand('cp', ['-R', os.path.join('dir0', 'dir1'),
                           suri(dst_bucket_uri, 'abc')], cwd=src_dir)
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'abc_$folder$'),
                    suri(dst_bucket_uri, 'abc', 'dir1', 'f1')])
    self.assertEqual(expected, actual)

  def testCopyingRelativePathSubDirToBucketSubdirSignifiedBySlash(self):
    """Tests recursively copying relative sub-directory to bucket subdir
    signified by a / object"""
    dst_bucket_uri = self.CreateBucket()
    src_dir = self.CreateTempDir(test_files=[('dir0', 'dir1', 'f1')])
    self.RunCommand('cp', ['-R', os.path.join('dir0', 'dir1'),
                           suri(dst_bucket_uri, 'abc') + '/'], cwd=src_dir)
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'abc', 'dir1', 'f1')])
    self.assertEqual(expected, actual)

  def testCopyingRelativePathSubDirToBucket(self):
    """Tests recursively copying relative sub-directory to a bucket"""
    dst_bucket_uri = self.CreateBucket()
    src_dir = self.CreateTempDir(test_files=[('dir0', 'dir1', 'f1')])
    self.RunCommand('cp', ['-R', os.path.join('dir0', 'dir1'),
                           suri(dst_bucket_uri)], cwd=src_dir)
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'dir1', 'f1')])
    self.assertEqual(expected, actual)

  def testCopyingDotSlashToBucket(self):
    """Tests copying ./ to a bucket produces expected naming"""
    # When running a command like gsutil cp -r . gs://dest we expect the dest
    # obj names to be of the form gs://dest/abc, not gs://dest/./abc.
    dst_bucket_uri = self.CreateBucket()
    src_dir = self.CreateTempDir(test_files=['foo'])
    for rel_src_dir in ['.', '.%s' % os.sep]:
      self.RunCommand('cp', ['-R', rel_src_dir, suri(dst_bucket_uri)],
                      cwd=src_dir)
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, '**')).IterUris())
      expected = set([suri(dst_bucket_uri, 'foo')])
      self.assertEqual(expected, actual)

  def testCopyingDirContainingOneFileToBucket(self):
    """Tests copying a directory containing 1 file to a bucket.
    We test this case to ensure that correct bucket handling isn't dependent
    on the copy being treated as a multi-source copy.
    """
    dst_bucket_uri = self.CreateBucket()
    src_dir = self.CreateTempDir(test_files=[('dir0', 'dir1', 'foo')])
    self.RunCommand('cp', ['-R', os.path.join(src_dir, 'dir0', 'dir1'),
                    suri(dst_bucket_uri)])
    actual = list((str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris()))
    self.assertEqual(1, len(actual))
    self.assertEqual(suri(dst_bucket_uri, 'dir1', 'foo'), actual[0])

  def testCopyingBucketToDir(self):
    """Tests copying from a bucket to a directory"""
    src_bucket_uri = self.CreateBucket(test_objects=['foo', 'dir/foo2'])
    dst_dir = self.CreateTempDir()
    self.RunCommand('cp', ['-R', suri(src_bucket_uri), dst_dir])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        '%s%s**' % (dst_dir, os.sep)).IterUris())
    expected = set([suri(dst_dir, src_bucket_uri.bucket_name, 'foo'),
                    suri(dst_dir, src_bucket_uri.bucket_name, 'dir', 'foo2')])
    self.assertEqual(expected, actual)

  def testCopyingBucketToBucket(self):
    """Tests copying from a bucket-only URI to a bucket"""
    src_bucket_uri = self.CreateBucket(test_objects=['foo', 'dir/foo2'])
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', ['-R', suri(src_bucket_uri), suri(dst_bucket_uri)])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([
        suri(dst_bucket_uri, src_bucket_uri.bucket_name, 'foo'),
        suri(dst_bucket_uri, src_bucket_uri.bucket_name, 'dir', 'foo2')])
    self.assertEqual(expected, actual)

  def testCopyingDirectoryToDirectory(self):
    """Tests copying from a directory to a directory"""
    src_dir = self.CreateTempDir(test_files=['foo', ('dir', 'foo2')])
    dst_dir = self.CreateTempDir()
    self.RunCommand('cp', ['-R', src_dir, dst_dir])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        '%s%s**' % (dst_dir, os.sep)).IterUris())
    src_dir_base = os.path.split(src_dir)[1]
    expected = set([suri(dst_dir, src_dir_base, 'foo'),
                    suri(dst_dir, src_dir_base, 'dir', 'foo2')])
    self.assertEqual(expected, actual)

  def testCopyingFilesAndDirNonRecursive(self):
    """Tests copying containing files and a directory without -R"""
    src_dir = self.CreateTempDir(test_files=['foo', 'bar', ('d1', 'f2'),
                                             ('d2', 'f3'), ('d3', 'd4', 'f4')])
    dst_dir = self.CreateTempDir()
    self.RunCommand('cp', ['%s%s*' % (src_dir, os.sep), dst_dir])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        '%s%s**' % (dst_dir, os.sep)).IterUris())
    expected = set([suri(dst_dir, 'foo'), suri(dst_dir, 'bar')])
    self.assertEqual(expected, actual)

  def testCopyingFileToDir(self):
    """Tests copying one file to a directory"""
    src_file = self.CreateTempFile(file_name='foo')
    dst_dir = self.CreateTempDir()
    self.RunCommand('cp', [src_file, dst_dir])
    actual = list(self._test_wildcard_iterator(
          '%s%s*' % (dst_dir, os.sep)).IterUris())
    self.assertEqual(1, len(actual))
    self.assertEqual(suri(dst_dir, 'foo'), actual[0].uri)

  def testCopyingFileToObjectWithConsecutiveSlashes(self):
    """Tests copying a file to an object containing consecutive slashes"""
    src_file = self.CreateTempFile(file_name='f0')
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', [src_file, suri(dst_bucket_uri) + '//obj'])
    actual = list(self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    self.assertEqual(1, len(actual))
    self.assertEqual('/obj', actual[0].object_name)

  def testCopyingCompressedFileToBucket(self):
    """Tests copying one file with compression to a bucket"""
    src_file = self.CreateTempFile(contents='plaintext', file_name='f2.txt')
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', ['-z', 'txt', src_file, suri(dst_bucket_uri)],)
    actual = list(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '*')).IterUris())
    self.assertEqual(1, len(actual))
    expected_dst_uri = dst_bucket_uri.clone_replace_name('f2.txt')
    self.assertEqual(expected_dst_uri.uri, actual[0])
    dst_key = expected_dst_uri.get_key()
    dst_key.open_read()
    self.assertEqual('gzip', dst_key.content_encoding)
    contents = dst_key.read()
    f = gzip.GzipFile(fileobj=StringIO.StringIO(contents), mode='rb')
    try:
      self.assertEqual(f.read(), 'plaintext')
    finally:
      f.close()

  def testCopyingObjectToObject(self):
    """Tests copying an object to an object"""
    src_bucket_uri = self.CreateBucket(test_objects=['obj'])
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', [suri(src_bucket_uri, 'obj'), suri(dst_bucket_uri)])
    actual = list(self._test_wildcard_iterator(
        suri(dst_bucket_uri, '*')).IterUris())
    self.assertEqual(1, len(actual))
    self.assertEqual('obj', actual[0].object_name)

  def testCopyingObjectToObjectUsingDestWildcard(self):
    """Tests copying an object to an object using a dest wildcard"""
    src_bucket_uri = self.CreateBucket(test_objects=['obj'])
    dst_bucket_uri = self.CreateBucket(test_objects=['dstobj'])
    self.RunCommand('cp', [suri(src_bucket_uri, 'obj'),
                    '%s*' % dst_bucket_uri.uri])
    actual = list(self._test_wildcard_iterator(
        suri(dst_bucket_uri, '*')).IterUris())
    self.assertEqual(1, len(actual))
    self.assertEqual('dstobj', actual[0].object_name)

  def testCopyingObjsAndFilesToDir(self):
    """Tests copying objects and files to a directory"""
    src_bucket_uri = self.CreateBucket(test_objects=['f1'])
    src_dir = self.CreateTempDir(test_files=['f2'])
    dst_dir = self.CreateTempDir()
    self.RunCommand('cp', ['-R', suri(src_bucket_uri, '**'),
                           os.path.join(src_dir, '**'), dst_dir])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        os.path.join(dst_dir, '**')).IterUris())
    expected = set([suri(dst_dir, 'f1'), suri(dst_dir, 'f2')])
    self.assertEqual(expected, actual)

  def testCopyingObjToDot(self):
    """Tests that copying an object to . or ./ downloads to correct name"""
    src_bucket_uri = self.CreateBucket(test_objects=['f1'])
    dst_dir = self.CreateTempDir()
    for final_char in ('/', ''):
      self.RunCommand('cp', [suri(src_bucket_uri, 'f1'), '.%s' % final_char],
                      cwd=dst_dir)
      actual = set()
      for dirname, dirnames, filenames in os.walk(dst_dir):
        for subdirname in dirnames:
          actual.add(os.path.join(dirname, subdirname))
        for filename in filenames:
          actual.add(os.path.join(dirname, filename))
      expected = set([os.path.join(dst_dir, 'f1')])
      self.assertEqual(expected, actual)

  def testCopyingObjsAndFilesToBucket(self):
    """Tests copying objects and files to a bucket"""
    src_bucket_uri = self.CreateBucket(test_objects=['f1'])
    src_dir = self.CreateTempDir(test_files=['f2'])
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', ['-R', suri(src_bucket_uri, '**'),
                           '%s%s**' % (src_dir, os.sep), suri(dst_bucket_uri)])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'f1'), suri(dst_bucket_uri, 'f2')])
    self.assertEqual(expected, actual)

  def testAttemptDirCopyWithoutRecursion(self):
    """Tests copying a directory without -R"""
    src_dir = self.CreateTempDir(test_files=1)
    dst_dir = self.CreateTempDir()
    try:
      self.RunCommand('cp', [src_dir, dst_dir])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('No URIs matched', e.reason)

  def testAttemptCopyingProviderOnlySrc(self):
    """Attempts to copy a src specified as a provider-only URI"""
    src_bucket_uri = self.CreateBucket()
    try:
      self.RunCommand('cp', ['gs://', suri(src_bucket_uri)])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('provider-only', e.reason)

  def testAttemptCopyingOverlappingSrcDstFile(self):
    """Attempts to an object atop itself"""
    src_file = self.CreateTempFile()
    try:
      self.RunCommand('cp', [src_file, src_file])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('are the same file - abort', e.reason)

  def testAttemptCopyingToMultiMatchWildcard(self):
    """Attempts to copy where dst wildcard matches >1 obj"""
    src_bucket_uri = self.CreateBucket()
    try:
      self.RunCommand('cp', [suri(src_bucket_uri, 'obj0'),
                             suri(src_bucket_uri, '*')])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertNotEqual(e.reason.find('must match exactly 1 URI'), -1)

  def testAttemptCopyingMultiObjsToFile(self):
    """Attempts to copy multiple objects to a file"""
    src_bucket_uri = self.CreateBucket(test_objects=2)
    dst_file = self.CreateTempFile()
    try:
      self.RunCommand('cp', ['-R', suri(src_bucket_uri, '*'), dst_file])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('must name a directory, bucket, or', e.reason)

  def testAttemptCopyingWithFileDirConflict(self):
    """Attempts to copy objects that cause a file/directory conflict"""
    # Create objects with name conflicts (a/b and a). Use 'dst' bucket because
    # it gets cleared after each test.
    bucket_uri = self.CreateBucket()
    self.CreateObject(bucket_uri=bucket_uri, object_name='a')
    self.CreateObject(bucket_uri=bucket_uri, object_name='b/a')
    dst_dir = self.CreateTempDir()
    try:
      self.RunCommand('cp', ['-R', suri(bucket_uri), dst_dir])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertNotEqual('exists where a directory needs to be created',
                          e.reason)

  def testAttemptCopyingWithDirFileConflict(self):
    """Attempts to copy an object that causes a directory/file conflict"""
    # Create an object that conflicts with dest subdir.
    tmpdir = self.CreateTempDir()
    os.mkdir(os.path.join(tmpdir, 'abc'))
    src_uri = self.CreateObject(object_name='abc', contents='bar')
    try:
      self.RunCommand('cp', [suri(src_uri), tmpdir + '/'])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertNotEqual('where the file needs to be created', e.reason)

  def testWildcardMoveWithinBucket(self):
    """Attempts to move using src wildcard that overlaps dest object.
    We want to ensure that this doesn't stomp the result data. See the
    comment starting with 'Expand wildcards before' in commands/mv.py
    for details.
    """
    dst_bucket_uri = self.CreateBucket(test_objects=['old'])
    self.RunCommand('mv', [suri(dst_bucket_uri, 'old*'),
                           suri(dst_bucket_uri, 'new')])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'new')])
    self.assertEqual(expected, actual)

  def testLsNonExistentObjectWithPrefixName(self):
    """Test ls of non-existent obj that matches prefix of existing objs"""
    # Use an object name that matches a prefix of other names at that level, to
    # ensure the ls subdir handling logic doesn't pick up anything extra.
    src_bucket_uri = self.CreateBucket()
    try:
      output = self.RunCommand('ls', [suri(src_bucket_uri, 'obj')],
                               return_stdout=True)
    except CommandException, e:
      self.assertIn('No such object', e.reason)

  def testLsBucketNonRecursive(self):
    """Test that ls of a bucket returns expected results"""
    src_bucket_uri = self.CreateBucket(test_objects=['foo1', 'd0/foo2',
                                                     'd1/d2/foo3'])
    output = self.RunCommand('ls', [suri(src_bucket_uri, '*')],
                             return_stdout=True)
    expected = set([suri(src_bucket_uri, 'foo1'),
                    suri(src_bucket_uri, 'd1', ':'),
                    suri(src_bucket_uri, 'd1', 'd2') + src_bucket_uri.delim,
                    suri(src_bucket_uri, 'd0', ':'),
                    suri(src_bucket_uri, 'd0', 'foo2')])
    expected.add('') # Blank line between subdir listings.
    actual = set(output.split('\n'))
    self.assertEqual(expected, actual)

  def testLsBucketRecursive(self):
    """Test that ls -R of a bucket returns expected results"""
    src_bucket_uri = self.CreateBucket(test_objects=['foo1', 'd0/foo2',
                                                     'd1/d2/foo3'])
    output = self.RunCommand('ls', ['-R', suri(src_bucket_uri, '*')],
                             return_stdout=True)
    expected = set([suri(src_bucket_uri, 'foo1'),
                    suri(src_bucket_uri, 'd1', ':'),
                    suri(src_bucket_uri, 'd1', 'd2', ':'),
                    suri(src_bucket_uri, 'd1', 'd2', 'foo3'),
                    suri(src_bucket_uri, 'd0', ':'),
                    suri(src_bucket_uri, 'd0', 'foo2')])
    expected.add('') # Blank line between subdir listings.
    actual = set(output.split('\n'))
    self.assertEqual(expected, actual)

  def testLsBucketRecursiveWithLeadingSlashObjectName(self):
    """Test that ls -R of a bucket with an object that has leading slash"""
    dst_bucket_uri = self.CreateBucket(test_objects=['f0'])
    output = self.RunCommand('ls', ['-R', suri(dst_bucket_uri) + '*'],
                             return_stdout=True)
    expected = set([suri(dst_bucket_uri, 'f0')])
    expected.add('') # Blank line between subdir listings.
    actual = set(output.split('\n'))
    self.assertEqual(expected, actual)

  def testLsBucketSubdirNonRecursive(self):
    """Test that ls of a bucket subdir returns expected results"""
    src_bucket_uri = self.CreateBucket(test_objects=['src_subdir/foo',
                                                     'src_subdir/nested/foo2'])
    output = self.RunCommand('ls', [suri(src_bucket_uri, 'src_subdir')],
                             return_stdout=True)
    expected = set([
        suri(src_bucket_uri, 'src_subdir', 'foo'),
        suri(src_bucket_uri, 'src_subdir', 'nested') + src_bucket_uri.delim])
    expected.add('') # Blank line between subdir listings.
    actual = set(output.split('\n'))
    self.assertEqual(expected, actual)

  def testLsBucketSubdirRecursive(self):
    """Test that ls -R of a bucket subdir returns expected results"""
    src_bucket_uri = self.CreateBucket(test_objects=['src_subdir/foo',
                                                     'src_subdir/nested/foo2'])
    for final_char in ('/', ''):
      output = self.RunCommand(
          'ls', ['-R', suri(src_bucket_uri, 'src_subdir') + final_char],
          return_stdout=True)
      expected = set([
        suri(src_bucket_uri, 'src_subdir', ':'),
        suri(src_bucket_uri, 'src_subdir', 'foo'),
        suri(src_bucket_uri, 'src_subdir', 'nested', ':'),
        suri(src_bucket_uri, 'src_subdir', 'nested', 'foo2')])
      expected.add('') # Blank line between subdir listings.
      actual = set(output.split('\n'))
      self.assertEqual(expected, actual)

  def testSetAclOnBucketRuns(self):
    """Test that the setacl command basically runs"""
    # We don't test reading back the acl (via getacl command) because at present
    # MockStorageService doesn't translate canned ACLs into actual ACL XML.
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('setacl', ['private', suri(src_bucket_uri)])

  def testSetAclOnWildcardNamedBucketRuns(self):
    """Test that setacl basically runs against wildcard-named bucket"""
    # We don't test reading back the acl (via getacl command) because at present
    # MockStorageService doesn't translate canned ACLs into actual ACL XML.
    src_bucket_uri = self.CreateBucket(test_objects=['f0'])
    self.RunCommand('setacl', ['private', suri(src_bucket_uri)[:-2] + '*'])

  def testSetAclOnObjectRuns(self):
    """Test that the setacl command basically runs"""
    src_bucket_uri = self.CreateBucket(test_objects=['f0'])
    self.RunCommand('setacl', ['private', suri(src_bucket_uri, '*')])

  def testSetDefAclOnBucketRuns(self):
    """Test that the setdefacl command basically runs"""
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('setdefacl', ['private', suri(src_bucket_uri)])

  def testSetDefAclOnObjectFails(self):
    """Test that the setdefacl command fails when run against an object"""
    src_bucket_uri = self.CreateBucket()
    try:
      self.RunCommand('setdefacl', ['private', suri(src_bucket_uri, '*')])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('URI must name a bucket', e.reason)

  def testMinusDOptionWorks(self):
    """Tests using gsutil -D option"""
    src_file = self.CreateTempFile(file_name='f0')
    dst_bucket_uri = self.CreateBucket()
    self.RunCommand('cp', [src_file, suri(dst_bucket_uri)], debug=3)
    actual = list(self._test_wildcard_iterator(
        suri(dst_bucket_uri, '*')).IterUris())
    self.assertEqual(1, len(actual))
    self.assertEqual('f0', actual[0].object_name)

  def DownloadTestHelper(self, func):
    """
    Test resumable download with custom test function to distort downloaded
    data. We expect an exception to be raised and the dest file to be removed.
    """
    object_uri = self.CreateObject()
    dst_dir = self.CreateTempDir()
    try:
      self.RunCommand('cp', [suri(object_uri), dst_dir], test_method=func)
      self.fail('Did not get expected CommandException')
    except CommandException:
      self.assertFalse(os.listdir(dst_dir))
    except:
      self.fail('Unexpected exception raised')

  def testDownloadWithObjectSizeChange(self):
    """
    Test resumable download on an object that changes size before the
    downloaded file's checksum is validated.
    """
    def append(fp):
      """Append a byte at end of an open file and flush contents."""
      fp.seek(0,2)
      fp.write('x')
      fp.flush()
    self.DownloadTestHelper(append)

  def testDownloadWithFileContentChange(self):
    """
    Tests resumable download on an object where the file content changes
    before the downloaded file's checksum is validated.
    """
    def overwrite(fp):
      """Overwrite first byte in an open file and flush contents."""
      fp.seek(0)
      fp.write('x')
      fp.flush()
    self.DownloadTestHelper(overwrite)

  def testFlatCopyingObjsAndFilesToBucketSubDir(self):
    """Tests copying flatly listed objects and files to bucket subdir"""
    src_bucket_uri = self.CreateBucket(test_objects=['f0', 'd0/f1', 'd1/d2/f2'])
    src_dir = self.CreateTempDir(test_files=['f3', ('d3', 'f4'),
                                             ('d4', 'd5', 'f5')])
    dst_bucket_uri = self.CreateBucket(test_objects=['dst_subdir0/existing',
                                                     'dst_subdir1/existing'])
    # Test with and without final slash on dest subdir.
    for i, final_char in enumerate(('/', '')):
      self.RunCommand(
          'cp', ['-R', suri(src_bucket_uri, '**'), os.path.join(src_dir, '**'),
                 suri(dst_bucket_uri, 'dst_subdir%d' % i) + final_char])

    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set()
    for i in range(2):
      expected.add(suri(dst_bucket_uri, 'dst_subdir%d' % i, 'existing'))
      for j in range(6):
        expected.add(suri(dst_bucket_uri, 'dst_subdir%d' % i, 'f%d' % j))
    self.assertEqual(expected, actual)

  def testRecursiveCopyObjsAndFilesToExistingBucketSubDir(self):
    """Tests recursive copy of objects and files to existing bucket subdir"""
    src_bucket_uri = self.CreateBucket(test_objects=['f0', 'nested/f1'])
    dst_bucket_uri = self.CreateBucket(test_objects=[
        'dst_subdir0/existing_obj', 'dst_subdir1/existing_obj'])
    src_dir = self.CreateTempDir(test_files=['f2', ('nested', 'f3')])
    # Test with and without final slash on dest subdir.
    for i, final_char in enumerate(('/', '')):
      self.RunCommand(
          'cp', ['-R', suri(src_bucket_uri), src_dir,
                 suri(dst_bucket_uri, 'dst_subdir%d' % i) + final_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, 'dst_subdir%d' % i, '**')).IterUris())
      tmp_dirname = os.path.split(src_dir)[1]
      bucketname = src_bucket_uri.bucket_name
      expected = set([
          suri(dst_bucket_uri, 'dst_subdir%d' % i, 'existing_obj'),
          suri(dst_bucket_uri, 'dst_subdir%d' % i, bucketname, 'f0'),
          suri(dst_bucket_uri, 'dst_subdir%d' % i, bucketname, 'nested', 'f1'),
          suri(dst_bucket_uri, 'dst_subdir%d' % i, tmp_dirname, 'f2'),
          suri(dst_bucket_uri, 'dst_subdir%d' % i, tmp_dirname, 'nested', 'f3')
      ])
      self.assertEqual(expected, actual)

  def testRecursiveCopyObjsAndFilesToNonExistentBucketSubDir(self):
    """Tests recursive copy of objs + files to non-existent bucket subdir"""
    src_bucket_uri = self.CreateBucket(test_objects=['f0', 'nested/f1'])
    src_dir = self.CreateTempDir(test_files=['f2', ('nested', 'f3')])
    dst_bucket_uri = self.CreateBucket()
    x = ['-R', src_dir, suri(src_bucket_uri),
               suri(dst_bucket_uri, 'dst_subdir')]
    stdout = self.RunCommand(
        'cp', x, return_stdout=True)
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'dst_subdir', 'f0'),
                    suri(dst_bucket_uri, 'dst_subdir', 'nested', 'f1'),
                    suri(dst_bucket_uri, 'dst_subdir', 'f2'),
                    suri(dst_bucket_uri, 'dst_subdir', 'nested', 'f3')])
    self.assertEqual(expected, actual)

  def testCopyingBucketSubDirToDir(self):
    """Tests copying a bucket subdir to a directory"""
    src_bucket_uri = self.CreateBucket(test_objects=['src_subdir/obj'])
    dst_dir = self.CreateTempDir()
    # Test with and without final slash on dest subdir.
    for (final_src_char, final_dst_char) in (
        ('', ''), ('', '/'), ('/', ''), ('/', '/') ):
      self.RunCommand(
          'cp', ['-R', suri(src_bucket_uri, 'src_subdir') + final_src_char,
                 dst_dir + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          '%s%s**' % (dst_dir, os.sep)).IterUris())
      expected = set([suri(dst_dir, 'src_subdir', 'obj')])
      self.assertEqual(expected, actual)

  def testCopyingWildcardSpecifiedBucketSubDirToExistingDir(self):
    """Tests copying a wildcard-specified bucket subdir to a directory"""
    src_bucket_uri = self.CreateBucket(
        test_objects=['src_sub0dir/foo', 'src_sub1dir/foo', 'src_sub2dir/foo',
                      'src_sub3dir/foo'])
    dst_dir = self.CreateTempDir()
    # Test with and without final slash on dest subdir.
    for i, (final_src_char, final_dst_char) in enumerate((
        ('', ''), ('', '/'), ('/', ''), ('/', '/') )):
      self.RunCommand(
          'cp', ['-R', suri(src_bucket_uri, 'src_sub%d*' % i) + final_src_char,
                 dst_dir + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          os.path.join(dst_dir, 'src_sub%ddir' % i, '**')).IterUris())
      expected = set([suri(dst_dir, 'src_sub%ddir' % i, 'foo')])
      self.assertEqual(expected, actual)

  def testCopyingBucketSubDirToDirFailsWithoutMinusR(self):
    """Tests for failure when attempting bucket subdir copy without -R"""
    src_bucket_uri = self.CreateBucket(test_objects=['src_subdir/obj'])
    dst_dir = self.CreateTempDir()
    try:
      self.RunCommand(
          'cp', [suri(src_bucket_uri, 'src_subdir'), dst_dir])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('does not exist', e.reason)

  def testCopyingBucketSubDirToBucketSubDir(self):
    """Tests copying a bucket subdir to another bucket subdir"""
    src_bucket_uri = self.CreateBucket(
        test_objects=['src_subdir_%d/obj' % i for i in range(4)])
    dst_bucket_uri = self.CreateBucket(
        test_objects=['dst_subdir_%d/obj2' % i for i in range(4)])
    # Test with and without final slash on dest subdir.
    for i, (final_src_char, final_dst_char) in enumerate((
        ('', ''), ('', '/'), ('/', ''), ('/', '/') )):
      self.RunCommand(
          'cp', ['-R', suri(src_bucket_uri, 'src_subdir_%d' % i) + final_src_char,
                 suri(dst_bucket_uri, 'dst_subdir_%d' % i) + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, 'dst_subdir_%d' % i, '**')).IterUris())
      expected = set([suri(dst_bucket_uri, 'dst_subdir_%d' % i,
                           'src_subdir_%d' % i, 'obj'),
                      suri(dst_bucket_uri, 'dst_subdir_%d' % i, 'obj2')])
      self.assertEqual(expected, actual)

  def testCopyingBucketSubDirToBucketSubDirWithNested(self):
    """Tests copying a bucket subdir to another bucket subdir with nesting."""
    src_bucket_uri = self.CreateBucket(
        test_objects=['src_subdir_%d/obj' % i for i in range(4)] +
                     ['src_subdir_%d/nested/obj' % i for i in range(4)])
    dst_bucket_uri = self.CreateBucket(
        test_objects=['dst_subdir_%d/obj2' % i for i in range(4)])
    # Test with and without final slash on dest subdir.
    for i, (final_src_char, final_dst_char) in enumerate((
        ('', ''), ('', '/'), ('/', ''), ('/', '/') )):
      self.RunCommand(
          'cp', ['-R', suri(src_bucket_uri, 'src_subdir_%d' % i) + final_src_char,
                 suri(dst_bucket_uri, 'dst_subdir_%d' % i) + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, 'dst_subdir_%d' % i, '**')).IterUris())
      expected = set([suri(dst_bucket_uri, 'dst_subdir_%d' % i,
                           'src_subdir_%d' % i, 'obj'),
                      suri(dst_bucket_uri, 'dst_subdir_%d' % i,
                           'src_subdir_%d' % i, 'nested', 'obj'),
                      suri(dst_bucket_uri, 'dst_subdir_%d' % i, 'obj2')])
      self.assertEqual(expected, actual)

  def testMovingBucketSubDirToExistingBucketSubDir(self):
    """Tests moving a bucket subdir to a existing bucket subdir"""
    src_objs = ['foo']
    for i in range(4):
      src_objs.extend(['src_subdir%d/foo2' % i, 'src_subdir%d/nested/foo3' % i])
    src_bucket_uri = self.CreateBucket(test_objects=src_objs)
    dst_bucket_uri = self.CreateBucket(
        test_objects=['dst_subdir%d/existing' % i for i in range(4)])
    # Test with and without final slash on dest subdir.
    for i, (final_src_char, final_dst_char) in enumerate((
        ('', ''), ('', '/'), ('/', ''), ('/', '/') )):
      self.RunCommand(
          'mv', [suri(src_bucket_uri, 'src_subdir%d' % i) + final_src_char,
                 suri(dst_bucket_uri, 'dst_subdir%d' % i) + final_dst_char])

    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set()
    for i in range(4):
      expected.add(suri(dst_bucket_uri, 'dst_subdir%d' % i, 'existing'))
      expected.add(suri(dst_bucket_uri, 'dst_subdir%d' % i, 'src_subdir%d' %i,
                        'foo2'))
      expected.add(suri(dst_bucket_uri, 'dst_subdir%d' % i, 'src_subdir%d' %i,
                        'nested', 'foo3'))
    self.assertEqual(expected, actual)

  def testCopyingObjectToBucketSubDir(self):
    """Tests copying an object to a bucket subdir"""
    src_bucket_uri = self.CreateBucket(test_objects=['obj0'])
    dst_bucket_uri = self.CreateBucket(test_objects=['dir0/existing',
                                                     'dir1/existing'])
    # Test with and without final slash on dest subdir.
    for i, final_dst_char in enumerate(('', '/')):
      self.RunCommand('cp', [
          suri(src_bucket_uri, 'obj0'),
          suri(dst_bucket_uri, 'dir%d' % i) + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, 'dir%d' % i, '**')).IterUris())
      expected = set([suri(dst_bucket_uri, 'dir%d' % i, 'obj0'),
                      suri(dst_bucket_uri, 'dir%d' % i, 'existing')])
      self.assertEqual(expected, actual)

  def testCopyingWildcardedFilesToBucketSubDir(self):
    """Tests copying wildcarded files to a bucket subdir"""
    dst_bucket_uri = self.CreateBucket(test_objects=['subdir0/existing',
                                                     'subdir1/existing'])
    src_dir = self.CreateTempDir(test_files=['f0', 'f1', 'f2'])
    # Test with and without final slash on dest subdir.
    for i, final_dst_char in enumerate(('', '/')):
      self.RunCommand(
          'cp', [os.path.join(src_dir, 'f?'),
                 suri(dst_bucket_uri, 'subdir%d' % i) + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, 'subdir%d' % i, '**')).IterUris())
      expected = set([suri(dst_bucket_uri, 'subdir%d' % i, 'existing'),
                      suri(dst_bucket_uri, 'subdir%d' % i, 'f0'),
                      suri(dst_bucket_uri, 'subdir%d' % i, 'f1'),
                      suri(dst_bucket_uri, 'subdir%d' % i, 'f2')])
      self.assertEqual(expected, actual)

  def testCopyingOneNestedFileToBucketSubDir(self):
    """Tests copying one nested file to a bucket subdir"""
    dst_bucket_uri = self.CreateBucket(test_objects=['d0/placeholder',
                                                     'd1/placeholder'])
    src_dir = self.CreateTempDir(test_files=[('d3', 'd4', 'nested', 'f1')])
    # Test with and without final slash on dest subdir.
    for i, final_dst_char in enumerate(('', '/')):
      self.RunCommand('cp', ['-r', suri(src_dir, 'd3'),
                             suri(dst_bucket_uri, 'd%d' % i) + final_dst_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(dst_bucket_uri, '**')).IterUris())
    expected = set([
      suri(dst_bucket_uri, 'd0', 'placeholder'),
      suri(dst_bucket_uri, 'd1', 'placeholder'),
      suri(dst_bucket_uri, 'd0', 'd3', 'd4', 'nested', 'f1'),
      suri(dst_bucket_uri, 'd1', 'd3', 'd4', 'nested', 'f1')])
    self.assertEqual(expected, actual)

  def testMovingWildcardedFilesToNonExistentBucketSubDir(self):
    """Tests moving files to a non-existent bucket subdir"""
    # This tests for how we allow users to do something like:
    #   gsutil cp *.txt gs://bucket/dir
    # where *.txt matches more than 1 file and gs://bucket/dir
    # doesn't exist as a subdir.
    #
    src_bucket_uri = self.CreateBucket(test_objects=[
        'f0f0', 'f0f1', 'f1f0', 'f1f1'])
    dst_bucket_uri = self.CreateBucket(test_objects=[
        'dst_subdir0/existing_obj', 'dst_subdir1/existing_obj'])
    # Test with and without final slash on dest subdir.
    for i, final_dst_char in enumerate(('', '/')):
      # Copy some files into place in dst bucket.
      self.RunCommand(
          'cp', [suri(src_bucket_uri, 'f%df?' % i),
                 suri(dst_bucket_uri, 'dst_subdir%d' % i) + final_dst_char])
      # Now do the move test.
      self.RunCommand(
          'mv', [suri(src_bucket_uri, 'f%d*' % i),
                 suri(dst_bucket_uri, 'nonexisting%d' % i) + final_dst_char])

    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([
      suri(dst_bucket_uri, 'dst_subdir0', 'existing_obj'),
      suri(dst_bucket_uri, 'dst_subdir0', 'f0f0'),
      suri(dst_bucket_uri, 'dst_subdir0', 'f0f1'),
      suri(dst_bucket_uri, 'nonexisting0', 'f0f0'),
      suri(dst_bucket_uri, 'nonexisting0', 'f0f1'),
      suri(dst_bucket_uri, 'dst_subdir1', 'existing_obj'),
      suri(dst_bucket_uri, 'dst_subdir1', 'f1f0'),
      suri(dst_bucket_uri, 'dst_subdir1', 'f1f1'),
      suri(dst_bucket_uri, 'nonexisting1', 'f1f0'),
      suri(dst_bucket_uri, 'nonexisting1', 'f1f1')])
    self.assertEqual(expected, actual)

  def testMovingObjectToBucketSubDir(self):
    """Tests moving an object to a bucket subdir"""
    src_bucket_uri = self.CreateBucket(test_objects=['obj0', 'obj1'])
    dst_bucket_uri = self.CreateBucket(test_objects=[
        'dst_subdir0/existing_obj', 'dst_subdir1/existing_obj'])
    # Test with and without final slash on dest subdir.
    for i, final_dst_char in enumerate(('', '/')):
      self.RunCommand(
          'mv', [suri(src_bucket_uri, 'obj%d' % i),
                 suri(dst_bucket_uri, 'dst_subdir%d' % i) + final_dst_char])

    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([
      suri(dst_bucket_uri, 'dst_subdir0', 'existing_obj'),
      suri(dst_bucket_uri, 'dst_subdir0', 'obj0'),
      suri(dst_bucket_uri, 'dst_subdir1', 'existing_obj'),
      suri(dst_bucket_uri, 'dst_subdir1', 'obj1')])
    self.assertEqual(expected, actual)

    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(src_bucket_uri, '**')).IterUris())
    self.assertEqual(actual, set())

  def testWildcardSrcSubDirMoveDisallowed(self):
    """Tests moving a bucket subdir specified by wildcard is disallowed"""
    src_bucket_uri = self.CreateBucket(test_objects=['dir/foo1'])
    dst_bucket_uri = self.CreateBucket(test_objects=['dir/foo2'])
    try:
      self.RunCommand(
          'mv', [suri(src_bucket_uri, 'dir*'), suri(dst_bucket_uri, 'dir')])
      self.fail('Did not get expected CommandException')
    except CommandException, e:
      self.assertIn('mv command disallows naming', e.reason)

  def testMovingBucketSubDirToNonExistentBucketSubDir(self):
    """Tests moving a bucket subdir to a non-existent bucket subdir"""
    src_bucket = self.CreateBucket(test_objects=[
        'foo', 'src_subdir0/foo2', 'src_subdir0/nested/foo3',
        'src_subdir1/foo2', 'src_subdir1/nested/foo3'])
    dst_bucket = self.CreateBucket()
    # Test with and without final slash on dest subdir.
    for i, final_src_char in enumerate(('', '/')):
      self.RunCommand(
          'mv', [suri(src_bucket, 'src_subdir%d' % i) + final_src_char,
                 suri(dst_bucket, 'dst_subdir%d' % i)])

    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket, '**')).IterUris())
    # Unlike the case with copying, with mv we expect renaming to occur
    # at the level of the src subdir, vs appending that subdir beneath the
    # dst subdir like is done for copying.
    expected = set([suri(dst_bucket, 'dst_subdir0', 'foo2'),
                    suri(dst_bucket, 'dst_subdir1', 'foo2'),
                    suri(dst_bucket, 'dst_subdir0', 'nested', 'foo3'),
                    suri(dst_bucket, 'dst_subdir1', 'nested', 'foo3')])
    self.assertEqual(expected, actual)

  def testRemovingBucketSubDir(self):
    """Tests removing a bucket subdir"""
    dst_bucket_uri = self.CreateBucket(test_objects=[
        'f0', 'dir0/f1', 'dir0/nested/f2', 'dir1/f1', 'dir1/nested/f2'])
    # Test with and without final slash on dest subdir.
    for i, final_src_char in enumerate(('', '/')):
      # Test removing bucket subdir.
      self.RunCommand(
          'rm', ['-R', suri(dst_bucket_uri, 'dir%d' % i) + final_src_char])
    actual = set(str(u) for u in self._test_wildcard_iterator(
        suri(dst_bucket_uri, '**')).IterUris())
    expected = set([suri(dst_bucket_uri, 'f0')])
    self.assertEqual(expected, actual)

  def testRecursiveRemoveObjsInBucket(self):
    """Tests removing all objects in bucket via rm -R gs://bucket"""
    bucket_uris = [
        self.CreateBucket(test_objects=['f0', 'dir/f1', 'dir/nested/f2']),
        self.CreateBucket(test_objects=['f0', 'dir/f1', 'dir/nested/f2'])]
    # Test with and without final slash on dest subdir.
    for i, final_src_char in enumerate(('', '/')):
      # Test removing all objects via rm -R.
      self.RunCommand('rm', ['-R', suri(bucket_uris[i]) + final_src_char])
      actual = set(str(u) for u in self._test_wildcard_iterator(
          suri(bucket_uris[i], '**')).IterUris())
      self.assertEqual(actual, set())

  def testUnicodeArgs(self):
    """Tests that you can list an object with unicode characters."""
    object_name = u'フォ'
    bucket_uri = self.CreateBucket()
    self.CreateObject(bucket_uri=bucket_uri, object_name=object_name,
                      contents='foo')
    object_name_bytes = object_name.encode('utf-8')
    stdout = self.RunCommand('ls', [suri(bucket_uri, object_name_bytes)],
                             return_stdout=True)
    self.assertIn(object_name_bytes, stdout)

  def FinalObjNameComponent(self, uri):
    """For gs://bucket/abc/def/ghi returns ghi."""
    return uri.uri.rpartition('/')[-1]


# TODO: These should all be moved to their own test_*.py testing files.
class GsUtilCommandTests(testcase.GsUtilUnitTestCase):
  """Basic sanity check tests to make sure commands run."""

  def testDisableLoggingCommandRuns(self):
    """Test that the disablelogging command basically runs"""
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('disablelogging', [suri(src_bucket_uri)])

  def testEnableLoggingCommandRuns(self):
    """Test that the enablelogging command basically runs"""
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('enablelogging', ['-b', 'gs://log_bucket',
                                      suri(src_bucket_uri)])

  def testHelpCommandDoesntRaise(self):
    """Test that the help command doesn't raise (sanity checks all help)"""
    # Unset PAGER if defined, so help output paginating into $PAGER doesn't
    # cause test to pause.
    if 'PAGER' in os.environ:
      del os.environ['PAGER']
    self.RunCommand('help', [])

  def testCatCommandRuns(self):
    """Test that the cat command basically runs"""
    src_uri = self.CreateObject(contents='foo')
    stdout = self.RunCommand('cat', [suri(src_uri)], return_stdout=True)
    self.assertEqual(stdout, 'foo')

  def testGetAclCommandRuns(self):
    """Test that the getacl command basically runs"""
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('getacl', [suri(src_bucket_uri)])

  def testGetDefAclCommandRuns(self):
    """Test that the getdefacl command basically runs"""
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('getacl', [suri(src_bucket_uri)])

  def testGetLoggingCommandRuns(self):
    """Test that the getlogging command basically runs"""
    src_bucket_uri = self.CreateBucket()
    self.RunCommand('getlogging', [suri(src_bucket_uri)])

  def testMakeBucketsCommand(self):
    """Test mb on existing bucket"""
    dst_bucket_uri = self.CreateBucket()
    try:
      self.RunCommand('mb', [suri(dst_bucket_uri)])
      self.fail('Did not get expected StorageCreateError')
    except boto.exception.StorageCreateError, e:
      self.assertEqual(e.status, 409)

  def testRemoveBucketsCommand(self):
    """Test rb on non-existent bucket"""
    dst_bucket_uri = self.CreateBucket()
    try:
      self.RunCommand(
          'rb', ['gs://non_existent_%s' % dst_bucket_uri.bucket_name])
      self.fail('Did not get expected StorageResponseError')
    except boto.exception.StorageResponseError, e:
      self.assertEqual(e.status, 404)

  def testRemoveObjsCommand(self):
    """Test rm command on non-existent object"""
    dst_bucket_uri = self.CreateBucket()
    try:
      self.RunCommand('rm', [suri(dst_bucket_uri, 'non_existent')])
      self.fail('Did not get expected WildcardException')
    except StorageResponseError, e:
      self.assertIn('Not Found', e.reason)

  # Now that gsutil ver computes a checksum it adds 1-3 seconds to test run
  # time (for in memory mocked tests that otherwise take ~ 0.1 seconds). Since
  # it provides very little test value, we're leaving this test commented out.
  #def testVerCommmandRuns(self):
  #  """Test that the Ver command basically runs"""
  #  self.RunCommand('ver', [])
