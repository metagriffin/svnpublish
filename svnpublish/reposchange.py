# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2009/09/22
# copy: (C) Copyright 2009-EOT metagriffin -- see LICENSE.txt
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
RepositoryChange represents a single changed object in a subversion
repository.
'''

#------------------------------------------------------------------------------
class RepositoryChange(object):
  # break-down of a content line:
  # first char: content disposition, one of:
  #     A  Added
  #     D  Deleted
  #     U  Updated
  #     C  Conflict
  #     G  Merged
  #     E  Existed
  # second char: property disposition, either none or U
  # third char: lock disposition, either none or B (B: broken)

  class Content:
    (NONE, ADDED, MODIFIED, DELETED, CONFLICT, MERGED, EXISTED) = range(7)
    codemap = {'_': NONE, 'A': ADDED, 'U': MODIFIED, 'D': DELETED, 'C': CONFLICT, 'G': MERGED, 'E': EXISTED}
    strmap  = {NONE: ' - ', ADDED: 'add', MODIFIED: 'mod', DELETED: 'del', CONFLICT: 'con', MERGED: 'mrg', EXISTED: 'exs'}

  class Property:
    # NOTE: currently subversion does not support property revisioning, so these are really nonsensical...
    (NONE, MODIFIED) = range(2)
    codemap = {' ': NONE, 'U': MODIFIED}
    strmap  = {NONE: ' - ', MODIFIED: 'mod'}

  def __init__(self, revinfo, line):
    self.revinfo    = revinfo
    self.svn        = revinfo.svn
    self.isdir      = line.endswith('/')
    self.path       = self.isdir and line[4:-1] or line[4:]
    self.content    = RepositoryChange.Content.codemap[line[0]]
    self.property   = RepositoryChange.Property.codemap[line[1]]
    self.proplist   = None

  # BEGIN: backwards compatibility
  # TODO: remove this
  def _getrepos(self):
    import warnings
    warnings.warn('RepositoryChange.repos has been deprecated - use RepositoryChange.svn.repos')
    return self.svn.repos
  repos = property(_getrepos)
  def _getrev(self):
    import warnings
    warnings.warn('RepositoryChange.rev has been deprecated - use RepositoryChange.revinfo.rev')
    return self.revinfo.rev
  rev = property(_getrev)
  # END: backwards compatibility

  def __cmp__(self, other):
    ret = cmp(self.path, other.path)
    if ret != 0:
      return ret
    return cmp(self.__dict__, other.__dict__)

  def __str__(self):
    return ( self.isdir and 'dir:  ' or 'file: ' ) \
           + ', '.join((RepositoryChange.Content.strmap[self.content],
                        RepositoryChange.Property.strmap[self.property],
                        self.path))

  def __repr__(self):
    return '<RepositoryChange path="{}" type="{}" content="{}" property="{}">'.format(
      self.path,
      'dir' if self.isdir else 'file',
      RepositoryChange.Content.strmap[self.content],
      RepositoryChange.Property.strmap[self.property],
      )

  def loadProperties(self):
    if self.proplist is not None: return
    self.proplist = {}
    pl = [ itm[2:] for itm in
           self.revinfo.svnlook('proplist', self.path).split('\n')
           if len(itm) > 0 ]
    for pkey in pl:
      pval = self.revinfo.svnlook('propget', pkey, self.path)
      self.proplist[pkey] = pval

  def getPropertyNames(self):
    self.loadProperties()
    return self.proplist.keys()

  def getProperty(self, key, default=None):
    self.loadProperties()
    return self.proplist.get(key, default)

  def isExecutable(self):
    # TODO: this should be converted to a dynamic attribute... getters are for java ijiots!
    return self.getProperty('svn:executable') is not None

  def isLink(self):
    # TODO: this should be converted to a dynamic attribute... getters are for java ijiots!
    return self.getProperty('svn:special', '') == '*'

  def getLinkTarget(self):
    if not self.isLink():
      raise LookupError('"%s" is not a link' % (self.path,))
    dat = self.getContent()
    if not dat.startswith('link '):
      # todo: this is probably not the right exception to raise...
      raise ValueError('unexpected error: "%s" did not contain a reference to a link')
    return dat[5:]

  def getContent(self):
    return self.revinfo.svnlook('cat', self.path)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
