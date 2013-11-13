# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2011/05/15
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

#------------------------------------------------------------------------------
# TODO: currently, this unit test actually writes to disk - this should be fixed
#       so that it uses the FileSystemOverlay... unfortunately that is a
#       monumental task, since the "export" engine relies heavily on system
#       calls.... ugh.
# TODO: use FSO!
#------------------------------------------------------------------------------

import sys, unittest, os, yaml, logging, six, shutil
from aadict import aadict

from svnpublish import framework, api, subversion, revinfo
from ..test_helper import TestCase, loadFileSystem, registerAllConfig

#------------------------------------------------------------------------------
class TestFingerprint(TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    super(TestFingerprint, self).setUp()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name     = 'testName'
    self.options.label    = 'testLabel'
    self.options.reposUrl = 'https://svn.example.com/repos'
    self.options.admin    = ['test@example.com']
    self.tmpdir           = '/tmp/svnpublish-unittest-engine-fingerprint'
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def tearDown(self):
    super(TestFingerprint, self).tearDown()
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def test_fingerprint_yaml(self):
    # todo: in the current way that publish_fingerprint writes to disk (using
    #      effectively system('tee ...'), i can only test what the output would
    #      have been, not the actual write, hence enabling "dryrun"... :( fix it!
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    self.options.dryrun      = True
    registerAllConfig('all', '''\
publish:
  - engine: fingerprint
    path:   ''' + self.tmpdir + '''/fp.yaml
    format: yaml
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.INFO)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertMultiLineEqual(self.logput.getvalue(), '''\
dry-run mode enabled: not executing any "write" actions
processing publishing point "content"
processing publishing point "content", engine "fingerprint"
loading engine "fingerprint" (callable: svnpublish.engine.fingerprint.publish_fingerprint)
dryrun: NOT creating fingerprint in "/tmp/svnpublish-unittest-engine-fingerprint/fp.yaml":
  'revision: 3\\nlast-published: 20090213T233130Z\\n'
''')

  #----------------------------------------------------------------------------
  def test_fingerprint_json(self):
    # todo: in the current way that publish_fingerprint writes to disk (using
    #      effectively system('tee ...'), i can only test what the output would
    #      have been, not the actual write, hence enabling "dryrun"... :( fix it!
    # TODO: use FSO!
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    self.options.dryrun      = True
    registerAllConfig('all', '''\
publish:
  - engine: fingerprint
    path:   ''' + self.tmpdir + '''/fp.json
    format: json
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.INFO)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertMultiLineEqual(self.logput.getvalue(), '''\
dry-run mode enabled: not executing any "write" actions
processing publishing point "content"
processing publishing point "content", engine "fingerprint"
loading engine "fingerprint" (callable: svnpublish.engine.fingerprint.publish_fingerprint)
dryrun: NOT creating fingerprint in "/tmp/svnpublish-unittest-engine-fingerprint/fp.json":
  '{\\n  "revision": 3,\\n  "last-published": "20090213T233130Z"\\n}\\n'
''')

  #----------------------------------------------------------------------------
  def test_fingerprint_custom(self):
    # todo: in the current way that publish_fingerprint writes to disk (using
    #      effectively system('tee ...'), i can only test what the output would
    #      have been, not the actual write, hence enabling "dryrun"... :( fix it!
    # TODO: use FSO!
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    self.options.dryrun      = True
    registerAllConfig('all', '''\
publish:
  - engine: fingerprint
    path:   ''' + self.tmpdir + '''/fp.txt
    format: \'myrev=%(revision)s\'
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.INFO)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertMultiLineEqual(self.logput.getvalue(), '''\
dry-run mode enabled: not executing any "write" actions
processing publishing point "content"
processing publishing point "content", engine "fingerprint"
loading engine "fingerprint" (callable: svnpublish.engine.fingerprint.publish_fingerprint)
dryrun: NOT creating fingerprint in "/tmp/svnpublish-unittest-engine-fingerprint/fp.txt":
  'myrev=3'
''')

  #----------------------------------------------------------------------------
  def test_fingerprint_fixate(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    tmpdir   = self.tmpdir
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine: export
    incremental: false
    path: ''' + tmpdir + '''
    fixate:
      - { engine: fingerprint, path: fp.json, format: \'rev%(revision)s.0\' }
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
              'file:/fp.json',
              'file:/textfile.txt',
              ]))
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))
    self.assertEqual(fs['/fp.json']['content'], 'rev4.0')

  #----------------------------------------------------------------------------
  def test_fingerprint_defaultpath(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    tmpdir   = self.tmpdir
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine: export
    incremental: false
    path: ''' + tmpdir + '''
    fixate:
      - { engine: fingerprint, format: \'rev%(revision)s.0\' }
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
              'file:/fingerprint',
              'file:/textfile.txt',
              ]))
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))
    self.assertEqual(fs['/fingerprint']['content'], 'rev4.0')

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
