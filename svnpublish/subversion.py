# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# desc: an abstraction for interfacing with svn
# auth: griffin <griffin@uberdev.org>
# date: 2011/04/28
# copy: (C) CopyLoose 2011 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The Subversion class encapsulates access to a subversion repository.

Note that the *revision* is always expected to be a string type, not an
integer, despite the current subversion revisions always being restricted
to being an integer.
'''

import sys

from . import api, revinfo, util

#------------------------------------------------------------------------------
# TODO: i hate this. it's a huge hack!
forceReposPath = []
def pushRepositoryOverride(path): forceReposPath.append(path)
def popRepositoryOverride(path):
  if path in forceReposPath: forceReposPath.remove(path)

#------------------------------------------------------------------------------
class Subversion(object):

  #----------------------------------------------------------------------------
  def __init__(self, repos):
    self.repos  = repos
    # minimum version is 1.4.6 (not really sure why. i think it's because that is
    # the version that i was using... ;)
    self.requireSvnlookVersion('1.4.6')

  #----------------------------------------------------------------------------
  def __repr__(self):
    return '<%s.%s: repos=%r>' % (self.__class__.__module__, self.__class__.__name__, self.repos)

  #----------------------------------------------------------------------------
  def __getstate__(self):
    return dict(repos=self.repos)

  #----------------------------------------------------------------------------
  def __setstate__(self, data):
    if len(forceReposPath) > 0:
      self.__init__(forceReposPath[-1])
    else:
      self.__init__(data['repos'])

  #----------------------------------------------------------------------------
  def svnlook(self, command, *args, **kwargs):
    'currently, kwargs must only contain the "revision" keyword'
    unwanted = set(kwargs.keys()).difference(set(['revision']))
    if len(unwanted) > 0:
      raise InvalidSvnlookKeywords(list(unwanted))
    newargs = []
    if command not in ['--version', 'help']:
      if 'revision' not in kwargs:
        raise InvalidSvnlookKeywords('"revision" parameter missing')
      newargs = [self.repos, '--revision', kwargs['revision']]
    newargs += args
    return util.run('svnlook', command, *newargs)

  #----------------------------------------------------------------------------
  def requireSvnlookVersion(self, version):
    'require a minimum svnlook *version*, which must be in the format "1.2.3".'
    curver = self.svnlook('--version')
    if not curver.startswith('svnlook, version '):
      raise api.IncompatibleSvnlookVersion(curver.split('\n')[0])
    curver = curver.split('\n')[0][17:].split('.')
    curver[0] = int(curver[0])
    curver[1] = int(curver[1])
    curver[2] = int(curver[2].split()[0])
    version = [int(v) for v in version.split('.')]
    if curver[0] < version[0] \
       or ( curver[0] == version[0] and curver[1] < version[1] ) \
       or ( curver[0] == version[0] and curver[1] == version[1] and curver[2] < version[2] ):
      raise api.IncompatibleSvnlookVersion('svnlook version too old: %s (minimum required: %s)' \
                                             % ('.'.join([str(v) for v in curver]),
                                                '.'.join([str(v) for v in version])))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
