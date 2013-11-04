# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: griffin <griffin@uberdev.org>
# date: 2011/05/15
# copy: (C) CopyLoose 2011 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------
# TODO: currently, this unit test actually writes to disk - this
#       should be fixed so that it uses FSO: unfortunately, that is a
#       monumental task, since the "export" engine uses a call to an
#       external process that writes to disk... ugh.
#------------------------------------------------------------------------------

# TODO: test many more `export` options...

import sys, unittest, os, yaml, logging, time, pickle, shutil, six
from aadict import aadict

from svnpublish import framework, subversion, revinfo
from ..test_helper import TestCase, loadFileSystem, registerAllConfig

#------------------------------------------------------------------------------
class TestExport(TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    super(TestExport, self).setUp()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name     = 'testName'
    self.options.label    = 'testLabel'
    self.options.reposUrl = 'https://svn.example.com/repos'
    self.options.admin    = ['test@example.com']
    self.tmpdir           = '/tmp/svnpublish-unittest-engine-export'
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def tearDown(self):
    super(TestExport, self).tearDown()
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def test_export(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    tmpdir   = self.tmpdir
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine: export
    incremental: false
    path: ''' + tmpdir + '''
    # symlink: ...
    # symlink-target: ...
    # keychain: ...
    # remote: ...
    # fixate: ...
    # fixate-env[+]: ...
    # fixate-host: ...
    # fixate-host-env[+]: ...
    # finalize: ...
    # finalize-env[+]: ...
    # archive: ...
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
              'file:/textfile.txt',]))
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))

  #----------------------------------------------------------------------------
  def test_export_symlink(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    tmpdir   = self.tmpdir
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine: export
    incremental: false
    path: ''' + tmpdir + '''/r%(revision)s
    symlink: ''' + tmpdir + '''/current
    symlink-target: r%(revision)s
    # keychain: ...
    # remote: ...
    # fixate: ...
    # fixate-env[+]: ...
    # fixate-host: ...
    # fixate-host-env[+]: ...
    # finalize: ...
    # finalize-env[+]: ...
    # archive: ...
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.DEBUG)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    fs = loadFileSystem(self.tmpdir, True)
    self.assertEqual(
      sorted([':'.join([e.type, e.path]) for e in fs.values()]),
      sorted(['link:/current',
              'dir:/r4',
              'dir:/r4/directory',
              'file:/r4/directory/textfile.txt',
              'file:/r4/textfile.txt',
              ]))
    self.assertMultiLineEqual(
      fs['/r4/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/r4/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))
    self.assertEqual(fs['/current']['content'], 'r4')

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
