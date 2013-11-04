# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: unit test for "shell" svnpublish engine module
# auth: griffin <griffin@uberdev.org>
# date: 2011/05/15
# copy: (C) CopyLoose 2011 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------
# TODO: currently, this unit test actually writes to disk - this should be fixed
#      so that it uses the FileSystemOverlay... unfortunately that is a
#      monumental task, since the "export" engine relies heavily on system
#      calls.... ugh.
#------------------------------------------------------------------------------

import sys, unittest, os, yaml, logging, six, shutil, genemail
from aadict import aadict

from svnpublish import framework, api, subversion, revinfo
from ..test_helper import TestCase, loadFileSystem, registerAllConfig

#------------------------------------------------------------------------------
class TestShell(TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    super(TestShell, self).setUp()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    self.sender = genemail.DebugSender()
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name     = 'testName'
    self.options.label    = 'testLabel'
    self.options.reposUrl = 'https://svn.example.com/repos'
    self.options.admin    = ['test@example.com']
    self.options.genemail.sender = self.sender
    self.tmpdir           = '/tmp/svnpublish-unittest-engine-shell'
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def tearDown(self):
    super(TestShell, self).tearDown()
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def test_shell_fixate(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine:      export
    incremental: false
    path:        ''' + self.tmpdir + '''
    fixate:      echo "revision is r%(revision)s" > $SVNPUBLISH_STAGE/foo
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    fs = loadFileSystem(self.tmpdir, True)
    self.assertEqual(
      sorted([':'.join([e.type, e.path]) for e in fs.values()]),
      sorted(['dir:/directory',
              'file:/directory/textfile.txt',
              'file:/foo',
              'file:/textfile.txt',
              ]))
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))
    self.assertEqual(fs['/foo']['content'], 'revision is r4\n')

  #----------------------------------------------------------------------------
  def test_shell_output(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine:      export
    incremental: false
    path:        ''' + self.tmpdir + '''
    fixate:      echo "revision is r%(revision)s"
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    chk_init = '''\
publishing point "/" not in options.publishOnly - skipping
processing publishing point "content"
processing publishing point "content", engine "export"
loading engine "export" (callable: svnpublish.engine.export.publish_export)
'''
    chk_term = '''\
loading fixate engine "shell" (svnpublish.engine.shell.fixate_shell)
running fixate shell command "echo "revision is r%(revision)s""
revision is r4

'''
    out = self.logput.getvalue()
    self.assertMultiLineEqual(out[:len(chk_init)], chk_init)
    self.assertMultiLineEqual(out[- len(chk_term):], chk_term)
    self.assertRegexpMatches(
      out[len(chk_init):- len(chk_term)],
      r'^tarball "svnpublish\.[a-f0-9]{40}\.[0-9]+"')

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
