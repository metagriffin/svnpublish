# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2011/04/29
# copy: (C) Copyright 2011-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------


import unittest, os, pickle

from . import subversion, revinfo, api

#------------------------------------------------------------------------------
class TestSubversion(unittest.TestCase):

  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    os.chdir(os.path.join(os.path.dirname(__file__)))

  #----------------------------------------------------------------------------
  def test_versionRequire_good(self):
    svn = subversion.Subversion(self.svnRepos)
    svn.requireSvnlookVersion('0.0.0')

  #----------------------------------------------------------------------------
  def test_versionRequire_bad(self):
    svn = subversion.Subversion(self.svnRepos)
    with self.assertRaises(api.IncompatibleSvnlookVersion):
      svn.requireSvnlookVersion('100.100.100')

  #----------------------------------------------------------------------------
  def test_changes_01(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.assertEqual(1, len(svnrev.changes))
    self.assertEqual('file: mod,  - , content/textfile.txt', str(svnrev.changes[0]))
    # update all
    svnrev.markAllUpdated()
    self.assertEqual(5, len(svnrev.changes))
    self.assertEqual([
      'dir:  mod, mod, /',
      'dir:  mod, mod, content',
      'dir:  mod, mod, content/directory',
      'file: mod, mod, content/directory/textfile.txt',
      'file: mod, mod, content/textfile.txt',
      ],[str(c) for c in svnrev.changes])
    # update a file
    svnrev.markAllUpdated('content/directory/textfile.txt')
    self.assertEqual(1, len(svnrev.changes))
    self.assertEqual('file: mod, mod, content/directory/textfile.txt', str(svnrev.changes[0]))
    # update a file (absolute reference)
    svnrev.markAllUpdated('/content/directory/textfile.txt')
    self.assertEqual(1, len(svnrev.changes))
    self.assertEqual('file: mod, mod, content/directory/textfile.txt', str(svnrev.changes[0]))
    # update a directory
    svnrev.markAllUpdated('content/directory')
    self.assertEqual(2, len(svnrev.changes))
    self.assertEqual([
      'dir:  mod, mod, content/directory',
      'file: mod, mod, content/directory/textfile.txt',
      ],[str(c) for c in svnrev.changes])
    # update a directory (absolute reference)
    svnrev.markAllUpdated('/content/directory')
    self.assertEqual(2, len(svnrev.changes))
    self.assertEqual([
      'dir:  mod, mod, content/directory',
      'file: mod, mod, content/directory/textfile.txt',
      ],[str(c) for c in svnrev.changes])
    # update a directory (absolute reference + trailing slash)
    svnrev.markAllUpdated('/content/directory/')
    self.assertEqual(2, len(svnrev.changes))
    self.assertEqual([
      'dir:  mod, mod, content/directory',
      'file: mod, mod, content/directory/textfile.txt',
      ],[str(c) for c in svnrev.changes])

  #----------------------------------------------------------------------------
  def test_reposchange_01(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    self.assertEqual(1, len(svnrev.changes))
    c = svnrev.changes[0]
    self.assertEqual(sorted(['svn:eol-style', 'svn:keywords']),
                     sorted(c.getPropertyNames()))
    self.assertEqual('Id Revision', c.getProperty('svn:keywords'))
    self.assertEqual('LF', c.getProperty('svn:eol-style'))
    self.assertEqual('this is a sample textfile.txt with changes.\n',
                     c.getContent())

  #----------------------------------------------------------------------------
  def test_pickle(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    chk = "ccopy_reg\n_reconstructor\np0\n(csvnpublish.revinfo\nRevisionInfo\np1\nc__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nS'svn'\np6\ng0\n(csvnpublish.subversion\nSubversion\np7\ng2\nNtp8\nRp9\n(dp10\nS'repos'\np11\nS'test/repos'\np12\nsbsS'rev'\np13\nS'4'\np14\nsb."
    self.assertMultiLineEqual(chk, pickle.dumps(svnrev))

  #----------------------------------------------------------------------------
  def test_unpickle(self):
    svnrev = pickle.loads("ccopy_reg\n_reconstructor\np0\n(csvnpublish.revinfo\nRevisionInfo\np1\nc__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nS'svn'\np6\ng0\n(csvnpublish.subversion\nSubversion\np7\ng2\nNtp8\nRp9\n(dp10\nS'repos'\np11\nS'test/repos'\np12\nsbsS'rev'\np13\nS'4'\np14\nsb.")
    self.assertEqual(1, len(svnrev.changes))
    c = svnrev.changes[0]
    self.assertEqual(sorted(['svn:eol-style', 'svn:keywords']),
                     sorted(c.getPropertyNames()))
    self.assertEqual('Id Revision', c.getProperty('svn:keywords'))
    self.assertEqual('LF', c.getProperty('svn:eol-style'))
    self.assertEqual('this is a sample textfile.txt with changes.\n',
                     c.getContent())

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
