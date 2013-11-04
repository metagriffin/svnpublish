# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/10/18
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import os, time, unittest, yaml
from aadict import aadict

from svnpublish import framework, api

#------------------------------------------------------------------------------
class UnknownFileSystemEntry(Exception): pass
def loadFileSystem(base, relpaths=False):
  ret = {}
  def collector(arg, dirname, names):
    relbase = (dirname + os.path.sep)[len(base):]
    for entry in names:
      path    = os.path.join(dirname, entry)
      relpath = relpaths and os.path.join(relbase, entry) or path
      if os.path.islink(path):
        ret[relpath] = aadict(path=relpath, type='link', content=os.readlink(path))
        continue
      if os.path.isfile(path):
        ret[relpath] = aadict(path=relpath, type='file', content=open(path, 'rb').read())
        continue
      if os.path.isdir(path):
        ret[relpath] = aadict(path=relpath, type='dir', content=None)
        continue
      raise UnknownFileSystemEntry(path)
  os.path.walk(base, collector, ret)
  return ret

#------------------------------------------------------------------------------
def registerAllConfig(name, config):
  class ConfigSourceAll(api.ConfigSource):
    def getConfig(self, root):
      return yaml.load(config)
  framework.sources.register(name, ConfigSourceAll)

#------------------------------------------------------------------------------
def stoptime(at=None):
  if at is None:
    at = time.time()
  at = float(at)
  if not hasattr(time, '__original_time__'):
    time.__original_time__ = time.time
  time.time = lambda: at
  return at

#------------------------------------------------------------------------------
def unstoptime():
  if hasattr(time, '__original_time__'):
    time.time = time.__original_time__

#------------------------------------------------------------------------------
class StopTimeMixin(object):
  '''
  IMPORTANT: this must be listed *before* unittest.TestCase, e.g.:
    class MyTestCase(StopTimeMixin, unittest.TestCase): ...
  '''
  def setUp(self):
    self.stoppedtime = stoptime(getattr(self, 'stoppedtime', None))
    super(StopTimeMixin, self).setUp()
  def tearDown(self):
    self.stoppedtime = None
    unstoptime()
    super(StopTimeMixin, self).tearDown()

#------------------------------------------------------------------------------
class TestCase(StopTimeMixin, unittest.TestCase):
  def setUp(self):
    self.stoppedtime = 1234567890.0 # == 2009-02-13T23:31:30Z
    super(TestCase, self).setUp()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
