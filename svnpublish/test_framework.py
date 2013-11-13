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

import sys, unittest, os, yaml, logging, six, genemail
from aadict import aadict

from . import framework, api, subversion, revinfo

class ConfigSourceNoSuchEngine(api.ConfigSource):
  def getConfig(self, root):
    return yaml.load('publish: [engine: no-such-engine]')
framework.sources.register('no-such-engine', ConfigSourceNoSuchEngine)

#------------------------------------------------------------------------------
class TestFramework(unittest.TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    os.chdir(os.path.join(os.path.dirname(__file__)))
    self.sender = genemail.DebugSender()
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name  = 'testName'
    self.options.label = 'testLabel'
    self.options.admin = ['test@example.com']
    self.options.genemail.sender = self.sender

  #----------------------------------------------------------------------------
  def test_pubpoint_001(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    pubpnts  = svnpub.loadPublishingPoints()
    # TODO: remove the sorted...
    self.assertEqual(['/', 'project', 'project/directory'], [p.root for p in pubpnts])

  #----------------------------------------------------------------------------
  def test_pubpoint_002(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    self.options.publishOnly = ['.*project$']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    pubpnts  = svnpub.loadPublishingPoints()
    self.assertEqual(['project'], [p.root for p in pubpnts])

  #----------------------------------------------------------------------------
  def test_pubpoint_003(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    self.options.publishOnly = ['t']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    pubpnts  = svnpub.loadPublishingPoints()
    self.assertEqual([], [p.root for p in pubpnts])

  #----------------------------------------------------------------------------
  def test_pubpoint_004(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    self.options.publishOnly = ['.*']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    pubpnts  = svnpub.loadPublishingPoints()
    self.assertEqual(['/', 'project', 'project/directory'], [p.root for p in pubpnts])

  #----------------------------------------------------------------------------
  def test_pubpoint_005(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    self.options.publishOnly = ['.*t.*']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    pubpnts  = svnpub.loadPublishingPoints()
    self.assertEqual(['project', 'project/directory'], [p.root for p in pubpnts])

  #----------------------------------------------------------------------------
  def test_pubpoint_006(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    self.options.publishOnly = ['.*t']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    pubpnts  = svnpub.loadPublishingPoints()
    self.assertEqual(['project'], [p.root for p in pubpnts])

  #----------------------------------------------------------------------------
  def test_config_noSuchEngine(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.ERROR)
    errcnt   = svnpub.run()
    chk = '''\
error svnpublish.api.EngineLoadError occurred (details at end)
error svnpublish.api.EngineLoadError occurred (details at end)
error svnpublish.api.EngineLoadError occurred (details at end)
======================================================================
'''
    self.assertMultiLineEqual(chk, self.logput.getvalue()[:len(chk)])
    self.assertEqual(3, errcnt)

  #----------------------------------------------------------------------------
  def test_config_override(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['no-such-engine']
    self.options.overrideConfig = 'data:text/plain;ascii,publish: [engine: echo]'
    svnpub   = framework.Framework(self.options, svnrev=svnrev)
    errcnt   = svnpub.run()
    self.assertEqual(0, errcnt)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
