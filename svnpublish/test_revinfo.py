# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish
# desc: unit test for svnpublish.revinfo module
# auth: griffin <griffin@uberdev.org>
# date: 2011/04/29
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest, os
from aadict import aadict

from . import subversion, revinfo, reposchange

#------------------------------------------------------------------------------
class TestRevinfo(unittest.TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    os.chdir(os.path.join(os.path.dirname(__file__)))

  #----------------------------------------------------------------------------
  def test_values(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.assertEqual('test/repos', svnrev.repository)
    self.assertEqual('1', svnrev.revision)
    self.assertEqual('svnuser', svnrev.author)
    self.assertEqual('2011-04-28 22:18:28 -0400 (Thu, 28 Apr 2011)', svnrev.date_svn)
    self.assertEqual(1304043508, svnrev.date_epoch)
    self.assertEqual('2011-04-29T02:18:28Z', svnrev.date)
    self.assertEqual('20110429T021828Z', svnrev.date_ts)
    self.assertEqual('2011-04-29T02:18:28+00:00', svnrev.date_iso)
    self.assertEqual('created an initial project hierarchy', svnrev.log)
    self.assertEqual('created an initial project hierarchy', svnrev.summary)
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'A   project/',
      'A   project/directory/',
      'A   project/directory/textfile.txt',
      'A   project/textfile.txt',
      ]]
    self.assertEqual(changes, svnrev.changes)
    self.assertEqual('''Added: project/directory/textfile.txt
===================================================================
--- project/directory/textfile.txt	                        (rev 0)
+++ project/directory/textfile.txt	2011-04-29 02:18:28 UTC (rev 1)
@@ -0,0 +1 @@
+this is another sample textfile.txt.


Property changes on: project/directory/textfile.txt
___________________________________________________________________
Added: svn:keywords
   + Id Revision

Added: project/textfile.txt
===================================================================
--- project/textfile.txt	                        (rev 0)
+++ project/textfile.txt	2011-04-29 02:18:28 UTC (rev 1)
@@ -0,0 +1 @@
+this is a sample textfile.txt.


Property changes on: project/textfile.txt
___________________________________________________________________
Added: svn:keywords
   + Id Revision

''', svnrev.diff)
    self.assertEqual([
      aadict(
        path   = 'project/directory/textfile.txt',
        target = 'content',
        diff   = '''Added: project/directory/textfile.txt
===================================================================
--- project/directory/textfile.txt	                        (rev 0)
+++ project/directory/textfile.txt	2011-04-29 02:18:28 UTC (rev 1)
@@ -0,0 +1 @@
+this is another sample textfile.txt.
'''
      ),
      aadict(
        path   = 'project/directory/textfile.txt',
        target = 'property',
        diff   = '''
Property changes on: project/directory/textfile.txt
___________________________________________________________________
Added: svn:keywords
   + Id Revision
'''),
      aadict(
        path   = 'project/textfile.txt',
        target = 'content',
        diff   = '''Added: project/textfile.txt
===================================================================
--- project/textfile.txt	                        (rev 0)
+++ project/textfile.txt	2011-04-29 02:18:28 UTC (rev 1)
@@ -0,0 +1 @@
+this is a sample textfile.txt.
'''),
      aadict(
        path   = 'project/textfile.txt',
        target = 'property',
        diff   = '''
Property changes on: project/textfile.txt
___________________________________________________________________
Added: svn:keywords
   + Id Revision
''')], svnrev.diff_set)

  #----------------------------------------------------------------------------
  def test_markAllUpdated_slash(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '6')
    svnrev.markAllUpdated('/')
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'UU  /',
      'UU  app/',
      'UU  app/README.txt',
      'UU  content/',
      'UU  content/directory/',
      'UU  content/directory/content.html.gst',
      'UU  content/directory/textfile.txt',
      'UU  content/textfile.txt',
      ]]
    self.assertEqual(changes, svnrev.changes)

  #----------------------------------------------------------------------------
  def test_markAllUpdated_nonoverlay(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '6')
    svnrev.markAllUpdated('content/directory')
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'UU  content/directory/',
      'UU  content/directory/content.html.gst',
      'UU  content/directory/textfile.txt',
      ]]
    self.assertEqual(changes, svnrev.changes)

  #----------------------------------------------------------------------------
  def test_markAllUpdated_overlay(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '6')
    svnrev.markAllUpdated('content/directory', overlay=True)
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'A   app/',
      'A   app/README.txt',
      'UU  content/directory/',
      'UU  content/directory/content.html.gst',
      'UU  content/directory/textfile.txt',
      ]]
    self.assertEqual(changes, svnrev.changes)

  #----------------------------------------------------------------------------
  def test_markUpdated_slash(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '6')
    svnrev.markUpdated('/')
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'UU  /',
      ]]
    self.assertEqual(changes, svnrev.changes)

  #----------------------------------------------------------------------------
  def test_markUpdated_nonoverlay(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '6')
    svnrev.markUpdated('content')
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'UU  content/',
      ]]
    self.assertEqual(changes, svnrev.changes)

  #----------------------------------------------------------------------------
  def test_markUpdated_overlay(self):
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '6')
    svnrev.markUpdated('content', overlay=True)
    changes = [reposchange.RepositoryChange(svnrev, line) for line in [
      'A   app/',
      'A   app/README.txt',
      'UU  content/',
      ]]
    self.assertEqual(changes, svnrev.changes)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
