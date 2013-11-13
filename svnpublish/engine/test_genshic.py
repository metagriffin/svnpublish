# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/2011/05/15
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
# TODO: currently, this unit test actually writes to disk - this
#       should be fixed so that it uses FSO: unfortunately, that is a
#       monumental task, since the "export" engine uses a call to an
#       external process that writes to disk... ugh.
#------------------------------------------------------------------------------

import unittest, os, six, logging, yaml, shutil, time
from aadict import aadict

from svnpublish import framework, revinfo, subversion
from ..test_helper import TestCase, loadFileSystem, registerAllConfig

#------------------------------------------------------------------------------
class TestGenshiCompile(TestCase):

  maxDiff  = None
  svnRepos = 'test/repos'

  #----------------------------------------------------------------------------
  def setUp(self):
    super(TestGenshiCompile, self).setUp()
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    self.logput = six.StringIO()
    self.log    = logging.getLogger()
    self.log.addHandler(logging.StreamHandler(self.logput))
    self.options  = aadict.d2ar(yaml.load(framework.defaultOptions))
    self.options.name     = 'testName'
    self.options.label    = 'testLabel'
    self.options.reposUrl = 'https://svn.example.com/repos'
    self.options.admin    = ['test@example.com']
    self.tmpdir           = '/tmp/svnpublish-unittest-engine-genshic'
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def tearDown(self):
    super(TestGenshiCompile, self).tearDown()
    if os.path.exists(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  #----------------------------------------------------------------------------
  def test_genshic_nada(self):
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
      - engine: genshic
        find: { iname: \'*.html.gst\' }
        delete-template: true
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.NOISE)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    fs = loadFileSystem(self.tmpdir, True)
    self.assertEqual(
      sorted([':'.join([e.type, e.path]) for e in fs.values()]),
      sorted([
        'dir:/directory',
        'file:/directory/textfile.txt',
        'file:/textfile.txt',
        ]))
    self.assertIn('no targets - done', self.logput.getvalue())
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))

  #----------------------------------------------------------------------------
  def test_genshic(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '5')
    tmpdir   = self.tmpdir
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine: export
    incremental: false
    path: ''' + tmpdir + '''
    fixate:
      - engine: genshic
        find: { iname: \'*.html.gst\' }
        delete-template: true
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.NOISE)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    fs = loadFileSystem(self.tmpdir, True)
    self.assertEqual(
      sorted([':'.join([e.type, e.path]) for e in fs.values()]),
      sorted([
        'dir:/directory',
        'file:/directory/content.html',
        'file:/directory/textfile.txt',
        'file:/textfile.txt',
        ]))
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))
    gstchk = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>
  <title>genshi-compile test</title>
 </head>
 <body>
  <div>$Id: content.html.gst 5 2011-05-26 04:10:16Z svnuser $</div>
  <div>Revision: 5</div>
  <div>Last published on: 20090213T233130Z</div>
 </body>
</html>\
'''
    self.assertMultiLineEqual(fs['/directory/content.html']['content'], gstchk)


  #----------------------------------------------------------------------------
  def test_genshi_compile_alias(self):
    svnrev   = revinfo.RevisionInfo(subversion.Subversion(self.svnRepos), '5')
    tmpdir   = self.tmpdir
    self.options.configOrder = ['all']
    self.options.publishOnly = ['content']
    registerAllConfig('all', '''\
publish:
  - engine: export
    incremental: false
    path: ''' + tmpdir + '''
    fixate:
      - engine: genshi-compile
        find: { iname: \'*.html.gst\' }
        delete-template: true
''')
    svnpub = framework.Framework(self.options, svnrev=svnrev)
    self.log.setLevel(logging.NOISE)
    errcnt = svnpub.run()
    self.assertEqual(errcnt, 0, 'svnpublish did not execute cleanly: ' + self.logput.getvalue())
    fs = loadFileSystem(self.tmpdir, True)
    self.assertEqual(
      sorted([':'.join([e.type, e.path]) for e in fs.values()]),
      sorted([
        'dir:/directory',
        'file:/directory/content.html',
        'file:/directory/textfile.txt',
        'file:/textfile.txt',
        ]))
    self.assertMultiLineEqual(
      fs['/directory/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/directory/textfile.txt'))
    self.assertMultiLineEqual(
      fs['/textfile.txt']['content'],
      svnrev.svnlook('cat', 'content/textfile.txt'))
    gstchk = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>
  <title>genshi-compile test</title>
 </head>
 <body>
  <div>$Id: content.html.gst 5 2011-05-26 04:10:16Z svnuser $</div>
  <div>Revision: 5</div>
  <div>Last published on: 20090213T233130Z</div>
 </body>
</html>\
'''
    self.assertMultiLineEqual(fs['/directory/content.html']['content'], gstchk)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
