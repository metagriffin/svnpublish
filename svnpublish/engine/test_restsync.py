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

# TODO: convert urllib2 to use six...

import sys, unittest, os, yaml, logging, six, fso, urllib2
from aadict import aadict

from svnpublish import framework, subversion, revinfo
from ..test_helper import TestCase, loadFileSystem, registerAllConfig

#------------------------------------------------------------------------------
# TODO: is there really no python package to do this???
# todo: move this into a separate package?
class FileHandler(urllib2.BaseHandler):
  def file_open(self, req, *args, **kwargs):
    if req.get_method().lower() == 'get':
      return open(req.get_selector(), 'rb')
    if req.get_method().lower() in ['put', 'post']:
      if not req.has_data():
        return open(req.get_selector(), 'wb')
      dirname = os.path.dirname(req.get_selector())
      if not os.path.exists(dirname):
        os.makedirs(dirname)
      with open(req.get_selector(), 'wb') as fp:
        fp.write(req.get_data())
      return open(req.get_selector(), 'rb')
    if req.get_method().lower() == 'delete':
      os.unlink(req.get_selector())
      # tbd: is this really the right thing to return?...
      return six.StringIO('')
    raise urllib2.URLError('unimplemented/unexpected method "%s"' % req.get_method())
  def ofile_open(self, req):
    return self.file_open(req)

#------------------------------------------------------------------------------
class TestRestsync(TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.setLevel(logging.DEBUG)
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name     = 'testName'
    self.options.label    = 'testLabel'
    self.options.reposUrl = 'https://svn.example.com/repos'
    self.options.admin    = ['test@example.com']
    self.fso = fso.push()
    self.tmpdir = '/tmp/svnpublish-unittest-engine-restsync'
    if not os.path.exists(self.tmpdir):
      os.makedirs(self.tmpdir)

  #----------------------------------------------------------------------------
  def tearDown(self):
    fso.pop()

  #----------------------------------------------------------------------------
  def test_restsync_put(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '3')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    self.options.urlHandlers = FileHandler
    registerAllConfig('all', '''\
publish:
  - engine: restsync
    remote-base: ofile://''' + self.tmpdir + '''/
    # request-filters: ...
    # includes: ...
    # excludes: ...
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.getChanges(self.tmpdir), [
      'add:',
      'add:textfile.txt',
      ])

  #----------------------------------------------------------------------------
  def test_restsync_put_attrchange(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '4')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    self.options.urlHandlers = FileHandler
    registerAllConfig('all', '''\
publish:
  - engine: restsync
    remote-base: ofile://''' + self.tmpdir + '''/
    # request-filters: ...
    # includes: ...
    # excludes: ...
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:' + self.tmpdir,
      ])

  #----------------------------------------------------------------------------
  def test_restsync_delete(self):
    # first, create the entries
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '1')
    self.options.configOrder = ['all']
    self.options.publishOnly = ['project']
    self.options.urlHandlers = FileHandler
    registerAllConfig('all', '''\
publish:
  - engine: restsync
    remote-base: ofile://''' + self.tmpdir + '''/
    # request-filters: ...
    # includes: ...
    # excludes: ...
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [
      'add:' + self.tmpdir,
      'add:' + os.path.join(self.tmpdir, 'directory'),
      'add:' + os.path.join(self.tmpdir, 'directory/textfile.txt'),
      'add:' + os.path.join(self.tmpdir, 'textfile.txt'),
      ])
    # second, delete the entries
    svnrev = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '2')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    self.assertEqual(self.fso.changes, [])

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
