# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: unit test for "echo" svnpublish engine module
# auth: griffin <griffin@uberdev.org>
# date: 2011/05/13
# copy: (C) CopyLoose 2011 UberDev <hardcore@uberdev.org>, No Rights Reserved.
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
