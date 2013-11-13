# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2011/05/13
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

from svnpublish import framework, api, subversion, revinfo

#------------------------------------------------------------------------------
class ConfigSourceAll(api.ConfigSource):
  def getConfig(self, root):
    return yaml.load('publish: [engine: echo]')
framework.sources.register('all', ConfigSourceAll)

#------------------------------------------------------------------------------
class TestEcho(unittest.TestCase):

  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
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
  def test_echo_info(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.INFO)
    errcnt = svnpub.run()
    self.assertEqual(0, errcnt, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertMultiLineEqual('''processing publishing point "content"
processing publishing point "content", engine "echo"
loading engine "echo" (callable: svnpublish.engine.echo.publish_echo)
publishing point "content":
  repository:    "test/repos"
  revision:      3
  admin:         test@example.com
''', self.logput.getvalue())

  #----------------------------------------------------------------------------
  def test_echo_debug(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(0, errcnt, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertMultiLineEqual('''publishing point "/" not in options.publishOnly - skipping
processing publishing point "content"
processing publishing point "content", engine "echo"
loading engine "echo" (callable: svnpublish.engine.echo.publish_echo)
publishing point "content":
  repository:    "test/repos"
  revision:      3
  admin:         test@example.com
  changes:
    file: mod,  - , content/textfile.txt
''', self.logput.getvalue())

  #----------------------------------------------------------------------------
  def test_echo_drivel(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DRIVEL)
    errcnt = svnpub.run()
    self.assertEqual(0, errcnt, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertMultiLineEqual('''checking change "file: mod,  - , content/textfile.txt" for publishing point config
publishing point "/" not in options.publishOnly - skipping
processing publishing point "content"
processing publishing point "content", engine "echo"
loading engine "echo" (callable: svnpublish.engine.echo.publish_echo)
publishing point "content":
  repository:    "test/repos"
  revision:      3
  admin:         test@example.com
  changes:
    file: mod,  - , content/textfile.txt
  diff:
    Modified: content/textfile.txt
    ===================================================================
    --- content/textfile.txt	2011-04-29 02:40:55 UTC (rev 2)
    +++ content/textfile.txt	2011-04-29 02:57:23 UTC (rev 3)
    @@ -1 +1 @@
    -this is a sample textfile.txt.
    +this is a sample textfile.txt with changes.
    
    
''', self.logput.getvalue())

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
