# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2009/09/02
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

# TODO: convert urllib2 to use six...

import sys, os, re, urllib2, hashlib, asset

from svnpublish.reposchange import RepositoryChange
from svnpublish.util import asList, run

#------------------------------------------------------------------------------
class NotInContext(Exception): pass
class RestError(Exception): pass
class RestSyncErrors(Exception): pass

#------------------------------------------------------------------------------
def publish_restsync_dryrun(params):
  return publish_restsync(params)

#------------------------------------------------------------------------------
def publish_restsync(params):
  '''
  Configurable parameters:

  :Parameters:

  TODO: add docs...

  urlHandlers : symbol-spec
  request-filters : dict
    callable : str
    args : dict
  '''


  # steps:
  #   - get list of objects to PUT and DELETE
  #   - order the DELETEs depth-first (so that files/subdirectories get
  #     deleted before the containing directories)

  # todo: should symlinks be copied?... the problem with that is that then
  #      any changes in the target need to be propagated into the symlink...
  # todo: what about fixations?...

  base = params.get('remote-base')
  if not base.endswith('/'):
    base += '/'

  params.logger.info('synchronizing to REST server: ' + base)
  dels = []
  puts = []
  for c in params.revinfo.changes:
    # (NONE, ADDED, MODIFIED, DELETED, CONFLICT, MERGED, EXISTED) = range(7)
    if c.content in [RepositoryChange.Content.ADDED,
                     RepositoryChange.Content.MODIFIED]:
      puts.append(c)
      continue
    if c.content in [RepositoryChange.Content.DELETED]:
      if not c.isdir:
        dels.append(c.path)
        continue
      # TODO: replace this with the svnlook() method?...
      #      or better yet, create a RevisionInfo.changes_explicit
      dels.extend(run('svnlook', 'tree', '--full-paths',
                      '--revision', str(int(params.revision) - 1),
                      params.repository, c.path).strip().split('\n'))
      continue
    params.logger.warn('ignoring unknown change type "%s" for entry "%s"'
                       % (RepositoryChange.Content.strmap[c.content], c.path))
    continue

  def delsort(a, b):
    if len(a) != len(b):
      if a.startswith(b):
        return -1
      if b.startswith(a):
        return 1
    if a.__gt__(b):
      return 1
    if a.__lt__(b):
      return -1
    return 0
  dels.sort(cmp=delsort)

  excludes = [re.compile(expr) for expr in asList(params.excludes)]
  includes = [re.compile(expr) for expr in asList(params.includes)]

  def syncPath(path):
    if params.root == path:
      relpath = ''
    else:
      if not path.startswith(params.root + '/'):
        raise NotInContext(params.root, path)
      relpath = path[len(params.root) + 1:]
    ret = True
    for e in excludes:
      if not e.search(relpath):
        continue
      ret = False
      break
    if ret: return relpath
    for i in includes:
      if not i.search(relpath):
        continue
      return relpath
    params.logger.debug('excluding %s%s' % (base, relpath))
    return None

  # load request decorator...
  # todo: perhaps it would be better to use the default opener...
  #      that way the unittest could just use that instead of this
  #      bogus urlHandler param...
  #opener = urllib2.OpenerDirector()
  #opener.add_handler(urllib2.HTTPCookieProcessor(cookieJar))
  opener = urllib2.build_opener(urllib2.HTTPHandler)
  opener.add_handler(urllib2.HTTPSHandler())
  for handler in asList(params.urlHandlers):
    opener.add_handler(asset.symbol(handler)())

  # TODO: i should enforce HTTPS certificate verification...
  
  filters = [aadict(spec=s) for s in asList(params.get('request-filters'))]
  for fltr in filters:
    # TODO: convert to use asset.symbol()... i.e.:
    #   fltr.handler = asset.symbol(fltr.spec.callable)
    modname = fltr.spec.callable.split(':')[0]
    module  = __import__(modname)
    if modname.find('.') >= 0:
      for n in modname.split('.')[1:]:
        module = getattr(module, n)
    fltr.handler = getattr(module, fltr.spec.callable.split(':')[1])

  errors = []

  for entry in dels:
    path = syncPath(entry)
    if path is None:
      continue
    url = '%s%s' % (base, path)
    while url.endswith('/'):
      url = url[:-1]
    if params.dryrun:
      params.logger.info('dry-run: DELETE: %s' % (url,))
      continue
    params.logger.debug('DELETE: %s' % (url,))
    try:
      request = urllib2.Request(url)
      request.add_header('Content-Type', 'application/octet-stream')
      request.get_method = lambda: 'DELETE'
      for fltr in filters:
        request = fltr.handler(request, **(fltr.spec.args))
      resp = opener.open(request)
    except urllib2.HTTPError, e:
      errors.append(RestError('DELETE', url, str(e.code) + ':' + e.msg))
    except urllib2.URLError, e:
      errors.append(RestError('DELETE', url, e.reason))

  for entry in puts:
    path = syncPath(entry.path)
    if path is None:
      continue
    url = '%s%s' % (base, path)
    if entry.isdir:
      continue
    if params.dryrun:
      params.logger.info('dry-run: PUT: %s' % (url,))
      continue
    data = entry.getContent()
    if entry.isLink():
      params.logger.warn('symlinks not supported: %s (to: %s)' % (url, data))
      errors.append(RestError('SYMLINK', url, 'not-supported'))
    params.logger.debug('PUT: %s (size: %i, md5: %s)' % (url, len(data), hashlib.md5(data).hexdigest()))
    try:
      request = urllib2.Request(url, data)
      request.add_header('Content-Type', 'application/octet-stream')
      request.get_method = lambda: 'PUT'
      for fltr in filters:
        request = fltr.handler(request, **(fltr.spec.args))
      resp = opener.open(request)
    except urllib2.HTTPError, e:
      errors.append(RestError('PUT', url, str(e.code) + ':' + e.msg))
    except urllib2.URLError, e:
      errors.append(RestError('PUT', url, e.reason))

  if len(errors) <= 0:
    return
  raise RestSyncErrors(errors)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
