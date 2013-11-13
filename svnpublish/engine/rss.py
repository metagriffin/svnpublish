# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2009/09/20
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

#------------------------------------------------------------------------------
# TODO: add support for generating articles that can be back-referenced:
#       note that i should NOT statically generate them, since that would
#       be a massive waste of space!...
# TODO: it would be nice if i could override the *styling* of the RSS
#       article instead of the structure... and on that note, it would be
#       great if i could define the structure using classes, and then inline
#       the styling (so that email browsers won't ignore the CSS)...
#------------------------------------------------------------------------------

'''
SvnPublish plugin that generates an atom (new RSS) feed with changes
to a repository. See http://tools.ietf.org/html/rfc4287.
'''

import sys, os, traceback, os.path, pickle, logging

from svnpublish import subversion, revinfo
from svnpublish.util import evalVars, aadict, tsl

#------------------------------------------------------------------------------
def publish_rss_dryrun(params):
  return publish_rss(params)

#------------------------------------------------------------------------------
def publish_rss(params):
  '''
  Configurable parameters:

  :Parameters:

  output : str
  feedUrl : str
  window : int, optional, default: 20
  params : dict, optional
  params+ : dict, optional
  params-item : dict, optional
  params-item+ : dict, optional
  onCacheError : str, optional, default: 'reload'
  reload : bool, optional, default: false

  TODO: add docs...
  '''

  if params.output is not None:
    # TODO: this should be done generically somewhere global...
    params.output = evalVars(params, params.output)

  if params.feedUrl is not None:
    # TODO: this should be done generically somewhere global...
    params.feedUrl = evalVars(params, params.feedUrl)

  revlist = load_revision_list(params)
  # TODO: warning! dependence on integer-based revisions...
  revlist.sort(cmp=lambda a,b: cmp(int(a.revision), int(b.revision)))
  params.logger.debug('loaded revisions: %s', ', '.join([str(ri.revision) for ri in revlist]))
  window = params.get('window', 20)
  if window > 0 and len(revlist) > window:
    revlist = revlist[0 - window:]
  if not params.dryrun:
    save_revision_list(params, revlist)

  params.logger.debug('processing revisions: %s', ', '.join([str(ri.revision) for ri in revlist]))

  tplitem = params.svnpub.talchemy['engine-rss']['item']
  tplfeed = params.svnpub.talchemy['engine-rss']['feed']

  tplitemVars = aadict(params.get('params-item') or {
    'params':  params,
    'publishDate': tsl(),
    }).update(params.get('params-item+') or {})

  tplVars = None

  if params.get('params') is not None:
    tplVars = aadict(params.params)
  else:
    class RssRevisionInfo(object):
      def __init__(self, revinfo):
        self.revinfo = revinfo
      def __getitem__(self, key):
        return self.__getattr__(key)
      def __getattr__(self, key):
        if key != 'feedContent':
          return getattr(self.revinfo, key)
        locVars = {}
        locVars.update(tplitemVars)
        if not locVars.has_key('revinfo'):
          locVars.update({'revinfo': self.revinfo})
        # TODO: do html inline-styling here...
        return tplitem.render('html', params=locVars)
        # return tplitem.generate(**locVars).render('html')
    tplVars = aadict({
      'revlist': [RssRevisionInfo(ri) for ri in revlist],
      'revinfo': params.revinfo,
      'params':  params,
      'publishDate': tsl(),
      })

  tplVars.update(params.get('params+') or {})

  # TODO: i *NEED* to create some way of generalizing this template handling
  #      so that all template rendering (eg fingerprint.py, email.py,
  #      genshi_compile.py) all share the same code... specifically, the
  #      parameters that are passed to the template.generate() method...

  out = tplfeed.render('xml', params=tplVars)

  if params.dryrun:
    params.logger.info('dry-run mode, not storing feed to "%s"', params.output)
    params.logger.log(logging.DRIVEL, '  feed content:')
    params.logger.log(logging.DRIVEL, '    ' + '\n    '.join(out.split('\n')))
    return

  params.logger.debug('updating rss feed in "%s"', params.output)

  with open(params.output, 'wb') as fp:
    fp.write(out)

#------------------------------------------------------------------------------
def load_revision_list(params):
  if params.reload == True:
    return load_revision_list_reload(params)
  picklepath = params.output + '.pkl'
  if not os.access(picklepath, os.R_OK):
    if params.get('onCacheError', 'reload') == 'reload':
      params.logger.info('no pickle file found - resorting to forced reload')
      return load_revision_list_reload(params)
    return [params.revinfo,]
  try:
    revlist = [params.revinfo,]
    params.logger.info('loading previous entries from pickled file')
    # todo: i would love to use "with...as" here, but that requires python 2.5+
    # TODO: ugh. this is a hack! basically, there is the potential for an svn
    #      repository to have moved... unfortunately the current de-pickling
    #      needs the correct info immediately...
    subversion.pushRepositoryOverride(params.revinfo.svn.repos)
    with open(picklepath, 'rb') as fp:
      revlist += pickle.load(fp)
    subversion.popRepositoryOverride(params.revinfo.svn.repos)
    # TODO: problem here is that the current window may be larger than the
    #      previous window...
    return revlist
  except Exception:
    et, ev = sys.exc_info()[:2]
    params.logger.error('pickle file loading failed:')
    params.logger.error('  %s.%s', et.__module__, traceback.format_exception_only(et, ev)[-1].strip())
    if params.get('onCacheError', 'reload') == 'reload':
      params.logger.info('resorting to forced reload')
      return load_revision_list_reload(params)
    return [params.revinfo,]

#------------------------------------------------------------------------------
def load_revision_list_reload(params):
  params.logger.info('forcing reload of all entries')
  revlist = [params.revinfo,]
  window = params.get('window', 20)
  rev = int(params.revinfo.revision) - 1
  while rev > 0:
    if window > 0 and len(revlist) >= window:
      break
    nextrevinfo = revinfo.RevisionInfo(params.svnpub.svnrev.svn, rev)
    nextrevinfo = revinfo.FilteredRevisionInfo(nextrevinfo, params.root)
    if len(nextrevinfo.changes) > 0:
      params.logger.debug('loaded revision %d', rev)
      revlist.append(nextrevinfo)
    else:
      params.logger.debug('not loading revision %d (no changes for this publishing point)', rev)
    rev -= 1
  return revlist

#------------------------------------------------------------------------------
def save_revision_list(params, revlist):
  picklepath = params.output + '.pkl'
  params.logger.info('saving revisions to "%s"', picklepath)
  if not os.path.exists(os.path.dirname(picklepath)):
    os.makedirs(os.path.dirname(picklepath))
  try:
    with open(picklepath, 'wb') as fp:
      pickle.dump(revlist, fp)
  except Exception:
    et, ev = sys.exc_info()[:2]
    params.logger.error('pickle file saving failed:')
    params.logger.error('  %s.%s', et.__module__, traceback.format_exception_only(et, ev)[-1].strip())

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
