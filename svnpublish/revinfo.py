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
RevisionInfo represents the information attached to a change in a
subversion repository.
'''

import sys, time, os
from aadict import aadict

from . import reposchange, util

#------------------------------------------------------------------------------
def parseSvnlookDate(s):
  # TODO: i am expecting the format:
  #        '2009-09-18 11:55:05 -0400 (Fri, 18 Sep 2009)'
  #          == '2009-09-18T15:55:05Z'
  #          == 1253289305
  #      verify that this is "spec" or not, but here it goes...
  tss = time.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
  # this "ts" is relative to the *local* machine... determine local offset...
  # (very important note: i must determine local offset AT THE TIME OF THE
  # TIMESTAMP!...)
  # TODO: THIS IS INSANE. THERE HAS GOT TO BE A BETTER WAY!... FRACK.
  tss0 = list(tss)
  tss0[8] = 0
  tss1 = list(time.gmtime(time.mktime(tss)))
  tss1[8] = 0
  offset = time.mktime(tss0) - time.mktime(tss1)
  # 'offset' is *this* machine's offset at the time of the timestamp
  t = time.mktime(tss) + offset
  t += ( s[20] == '-' and 1 or -1 ) * ( int(s[21:23]) * 3600 + int(s[23:25]) * 60 )
  return t

#------------------------------------------------------------------------------
def lines2diffset(lines):
  # todo: not doing much validation here...
  ret = aadict(diff='\n'.join(lines))
  if lines[0] != '' and lines[1] == ( '=' * 67 ):
    # this is a content diff
    ret.target = 'content'
    # todo: create other attributes, such as change type (added/modified/deleted)?
    ret.path = lines[0][lines[0].index(':') + 2:]
    return ret
  if lines[0] == '' and lines[1].startswith('Property changes on: ') and lines[2] == ( '_' * 67 ):
    ret.target = 'property'
    # todo: create other attributes, such as change type (added/modified/deleted)?
    ret.path = lines[1][21:]
    return ret
  raise api.InvalidSvnlookDiff('invalid diff type')
def parseSvnlookDiff(diff):
  # expected format of an svnlook diff:
  #   content changes:
  #     'Deleted|Added|Modfied: path
  #     =*67
  #     content
  #     <blank>
  #     '
  #   prop changes:
  #     '<blank>
  #     Property changes on: path
  #     _*67
  #     Added|Deleted: propname
  #        +|- content<newline>
  #     <blank>
  #     '
  if diff is None or len(diff) <= 0:
    return []
  ret = []
  cur = 0
  inContent = False
  inProperty = False
  lines = diff.split('\n')
  for idx, line in enumerate(lines):
    if inContent:
      if line != '': continue
      ret.append(lines2diffset(lines[cur:idx + 1]))
      cur = idx + 1
      inContent = False
      continue
    if inProperty:
      if line != '': continue
      if line == '' and idx == cur: continue
      if idx + 2 >= len(lines) \
         or ( idx + 2 < len(lines) and lines[idx + 1] != '' and lines[idx + 2] == '=' * 67 ) \
         or ( idx + 3 < len(lines) and lines[idx + 1] == '' and lines[idx + 2] != '' and lines[idx + 3] == '_' * 67 ):
        ret.append(lines2diffset(lines[cur:idx + 1]))
        cur = idx + 1
        inProperty = False
        continue
      continue
    # todo : i should regex-match line...
    if line != '' and idx + 1 < len(lines) and lines[idx + 1] == '=' * 67:
      inContent = True
      continue
    # todo : i should regex-match lines[idx + 1]
    if line == '' and idx + 2 < len(lines) and lines[idx + 1] != '' and lines[idx + 2] == '_' * 67:
      inProperty = True
      continue
    if line == '' and idx + 1 == len(lines) and idx == cur: continue
    raise api.InvalidSvnlookDiff('unexpected line %d format "%s"' % (idx + 1, line))
  if inContent:
    raise api.InvalidSvnlookDiff('no content change terminator')
  if inProperty:
    raise api.InvalidSvnlookDiff('no property change terminator')
  return ret

#------------------------------------------------------------------------------
def uniclean(data):
  # svnlook version 1.4.6 (and presumably earlier) would happily return
  # non-unicode data in the "log" and "diff"... so, handling it here.
  # TODO: i really should only do this if svnlook --version returns < 1.6.4
  try:
    unicode(data)
    return data
  except:
    return unicode(data, errors='ignore').encode()

#------------------------------------------------------------------------------
class RevisionInfo(object):
  def __init__(self, subversion, rev):
    self.__dict__['svn'] = subversion
    self.__dict__['rev'] = str(rev)
  def __repr__(self):
    return '<%s.%s: svn=%r, rev=%s>' % (
      self.__class__.__module__, self.__class__.__name__, self.svn, self.rev)
  def __getstate__(self):
    # pickle'ing
    return dict(svn=self.svn, rev=self.rev)
  def __setstate__(self, data):
    # de-pickle'ing
    self.__init__(data['svn'], data['rev'])
  def _cache(self, key, func):
    if key not in self.__dict__:
      self.__dict__[key] = func()
    return self.__dict__[key]
  def _changes(self):
    return self._cache('changes', lambda: self._uncached_changes())
  def _uncached_changes(self):
    if str(self.rev) == '0': return []
    changes = []
    for line in self.svnlook('changed').split('\n'):
      if len(line) < 4:
        continue
      ch = reposchange.RepositoryChange(self, line)
      changes.append(ch)
    return sorted(changes)
  def svnlook(self, *args, **kwargs):
    return self.svn.svnlook(revision=self.rev, *args, **kwargs)
  def markAllUpdated(self, path='/', overlay=False):
    # TODO: should i store this somewhere such that a de/serialization roundtrip works?
    if str(self.rev) == '0':
      return
    if overlay:
      changes = {chg.path: chg for chg in self.changes}
    else:
      changes = dict()
    args = ['--full-paths']
    path = os.path.normpath(path)
    if path.startswith('/'):
      path = path[1:]
    if len(path) > 0:
      args.append(path)
    for line in self.svnlook('tree', *args).split('\n'):
      if len(line) <= 0 or line in changes:
        continue
      changes[line] = reposchange.RepositoryChange(self, 'UU  ' + line)
    self.__dict__['changes'] = sorted(changes.values())
  def markUpdated(self, path='/', overlay=False):
    # TODO: should i store this somewhere such that a de/serialization roundtrip works?
    if str(self.rev) == '0':
      return
    if overlay:
      changes = {chg.path: chg for chg in self.changes}
    else:
      changes = dict()
    args = ['--full-paths']
    path = os.path.normpath(path)
    if path.startswith('/'):
      path = path[1:]
    if len(path) > 0:
      args.append(path)
    if path == '':
      path = '/'
    for line in self.svnlook('tree', *args).split('\n'):
      if len(line) <= 0 or line in changes or os.path.normpath(line) != path:
        continue
      changes[line] = reposchange.RepositoryChange(self, 'UU  ' + line)
    self.__dict__['changes'] = sorted(changes.values())
  def _repository(self): return self.svn.repos
  def _revision(self):   return self.rev
  def _author(self):     return self._cache('author',     lambda: self.svnlook('author').strip())
  def _date_svn(self):   return self._cache('date_svn',   lambda: self.svnlook('date').strip())
  def _date_epoch(self): return self._cache('date_epoch', lambda: parseSvnlookDate(self.date_svn))
  def _date(self):       return self._cache('date',       lambda: util.tsl(self.date_epoch))
  def _date_ts(self):    return self._cache('date_ts',    lambda: util.ts(self.date_epoch))
  def _date_iso(self):   return self._cache('date_iso',   lambda: util.ts_iso(self.date_epoch))
  def _log(self):        return self._cache('log',        lambda: uniclean(self.svnlook('log')).strip())
  def _diff(self):       return self._cache('diff',       lambda: uniclean(self.svnlook('diff')))
  def _diff_set(self):   return self._cache('diff_set',   lambda: parseSvnlookDiff(self.diff))
  def _summary(self):
    return self._cache(
      'summary',
      lambda: (len(self.log) == 0 and ['(none)',] or
               ( len(self.log) <= 60 and [self.log,] or [self.log[:40] + '...',]))[0])
  changes    = property(_changes)
  repository = property(_repository)
  revision   = property(_revision)
  author     = property(_author)
  date_svn   = property(_date_svn)
  date_epoch = property(_date_epoch)
  date       = property(_date)
  date_ts    = property(_date_ts)
  date_iso   = property(_date_iso)
  log        = property(_log)
  diff       = property(_diff)
  diff_set   = property(_diff_set)
  summary    = property(_summary)
  def __setattr__(self, key, val):
    # this should never be called...
    raise AttributeError(key)

#------------------------------------------------------------------------------
class FilteredRevisionInfo(object):
  '''filters the "changes", "diff" and "diff_set" attributes of a RevisionInfo
  object for a publishing point root directory'''
  def __init__(self, parent, root):
    self.__dict__['parent'] = parent
    self.__dict__['root']   = root
  def __repr__(self):
    return '<%s.%s: parent=%r, root=%r>' % (
      self.__class__.__module__, self.__class__.__name__, self.parent, self.root)
  def __getstate__(self):
    # pickle'ing
    return dict(parent=self.__dict__['parent'], root=self.__dict__['root'])
  def __setstate__(self, data):
    # de-pickle'ing
    self.__init__(data['parent'], data['root'])
  def containsPath(self, path):
    root = self.__dict__['root']
    if root == '/' or root == path:
      return True
    if not path.startswith(root):
      return False
    if not root.endswith('/') and path[len(root)] != '/':
      return False
    return True
  def __getattr__(self, key, defval=None):
    return getattr(self.__dict__['parent'], key, defval)
  def _cache(self, key, func):
    if key not in self.__dict__:
      self.__dict__[key] = func()
    return self.__dict__[key]
  def _changes(self):
    return self._cache(
      'changes',
      lambda: [e for e in self.__dict__['parent'].changes if self.containsPath(e.path)])
  def _diff(self):
    if len(self.changes) == len(self.__dict__['parent'].changes):
      return self.__dict__['parent'].diff
    return self._cache('diff', lambda: '\n'.join([e.diff for e in self.diff_set]))
  def _diff_set(self):
    if len(self.changes) == len(self.__dict__['parent'].changes):
      return self.__dict__['parent'].diff_set
    return self._cache('diff_set', lambda: [e for e in self.__dict__['parent'].diff_set if self.containsPath(e.path)])
  changes    = property(_changes)
  diff       = property(_diff)
  diff_set   = property(_diff_set)
  def __setattr__(self, key, val):
    # this should never be called...
    raise AttributeError(key)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
