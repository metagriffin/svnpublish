# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2011/04/28
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
