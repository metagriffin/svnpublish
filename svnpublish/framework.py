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
The svnpublish.framework module is the main execution framework for
``svnpublish`` -- it operates as the "clearinghouse" for engines,
configurations, and managers.

The framework expects to be given an ``aadict`` structure that provides
the options controlling the operating environment, which can have the
following attributes, expressed here as an example YAML file::

  .. include:: ./res/options.yaml
'''

# TODO: the exception handling in the Framework class is a bit... uh...
#       horrific. refactor!

import sys, os, logging, traceback, operator, yaml, re
import pkg_resources, setuptools, setuptools.package_index
import templatealchemy as ta
from aadict import aadict
from asset import isstr, symbol

from . import util, api
from .revinfo import FilteredRevisionInfo
from .util import asList, str2sym, autoresolve, flatten

#------------------------------------------------------------------------------

defaultOptions = util.getResourceString('options.yaml')
version = pkg_resources.get_distribution('svnpublish').version

#------------------------------------------------------------------------------
class SourceRegistry(object):
  def __init__(self):
    self.sources = dict()
  def register(self, name, factory):
    self.sources[name] = factory
  def get(self, name):
    if name not in self.sources:
      raise api.UnknownConfigSource(name)
    return self.sources[name]
sources = SourceRegistry()

#------------------------------------------------------------------------------
class ConfigSourceSvn(api.ConfigSource):
  def getConfig(self, name):
    try:
      ypath = os.path.join(name, self.svnpub.options.configPath)
      cfg = self.svnpub.svnrev.svnlook('cat', ypath)
      self.svnpub.log.debug(
        'loaded publishing point "%s" subversion config: "svn://%s"',
        name, ypath)
      return yaml.load(cfg)
    except api.CommandFailed:
      return None
sources.register('svn', ConfigSourceSvn)

#------------------------------------------------------------------------------
class ConfigSourceFs(api.ConfigSource):
  def getConfig(self, name):
    ypath = os.path.join(
      self.svnpub.options.configDir,
      name,
      self.svnpub.options.configPath)
    if not os.access(ypath, os.R_OK):
      return None
    self.svnpub.log.debug(
      'loaded publishing point "%s" filesystem config: "file://%s"',
      name, os.path.abspath(ypath))
    return yaml.load(open(ypath, 'rb'))
sources.register('fs', ConfigSourceFs)

#------------------------------------------------------------------------------
class PublishingPoint(object):
  def __init__(self, svnpub, root, config):
    self.svnpub  = svnpub
    self.root    = root or '/'
    self.config  = aadict(self.svnpub.options).update(config)
    self.revinfo = FilteredRevisionInfo(self.svnpub.svnrev, self.root)
    # pre-process some configuration items...
    self.config.admin = \
      list(set(asList(self.svnpub.options.admin) + asList(self.config.admin)))
    for engcfg in asList(self.config.publish):
      engcfg.admin = list(set(self.config.admin + asList(engcfg.admin)))

#------------------------------------------------------------------------------
class Framework(object):

  #----------------------------------------------------------------------------
  def __init__(self, options, svnrev=None, emailmanager=None):
    self.log          = logging.getLogger('svnpublish.framework')
    self.options      = options
    self.normalizeOptions()
    self.svnrev       = svnrev
    self.genemail     = autoresolve(options.genemail)
    self.talchemy     = ta.Registry(settings=flatten(options.templatealchemy))

  #----------------------------------------------------------------------------
  @property
  def version(self):
    return version

  #----------------------------------------------------------------------------
  def normalizeOptions(self):
    # TODO: use a normalization language to do this?...
    self.options.admin = asList(self.options.admin)
    # self.options.genshiPath = asList(self.options.genshiPath)
    # if self.options.smtpPort is not None:
    #   self.options.smtpPort = int(self.options.smtpPort)
    if self.options.engines is None:
      self.options.engines = aadict()

  #----------------------------------------------------------------------------
  def run(self):
    errors = {}
    # add global libraries to lookup path (note that per-publishing point
    # paths may be added later)
    for path in asList(self.options.libdir):
      self.log.info('adding "%s" to global system library path' % path)
      sys.path.append(path)
    if self.options.dryrun:
      self.log.warn('dry-run mode enabled: not executing any "write" actions')
    pubpnts = self.loadPublishingPoints()
    for pubpnt in pubpnts:
      # todo: this sys.path modification would better be done with "with ... do ..."
      #      but that requires python 2.5+... :(
      pubpntpath = sys.path[:]
      # TODO: the publishing points should be executed in parallel threads...
      try:
        self.log.info('processing publishing point "%s"', pubpnt.root)
        sys.path += asList(pubpnt.config.libdir)
        for engine in asList(pubpnt.config.publish):
          enginepath = sys.path[:]
          try:
            self.log.info('processing publishing point "%s", engine "%s"', pubpnt.root, engine.engine)
            sys.path += asList(engine.libdir)
            self.execPublishingPointEngine(pubpnt, engine)
          except Exception:
            err = sys.exc_info()
            self.log.error('error %s.%s occurred (details at end)', err[0].__module__, err[0].__name__)
            if not errors.has_key(pubpnt.root):
              errors[pubpnt.root] = []
            errors[pubpnt.root].append(err)
          sys.path = enginepath
      except Exception:
        err = sys.exc_info()
        self.log.error('error %s.%s occurred (details at end)', err[0].__module__, err[0].__name__)
        if not errors.has_key(pubpnt.root):
          errors[pubpnt.root] = []
        errors[pubpnt.root].append(err)
      sys.path = pubpntpath
    if len(errors) <= 0:
      return 0
    tot_errors = sum([len(i) for i in errors.values()])
    self.log.error('='*70)
    self.log.error('svnpublish failed with a total of %d error(s)', tot_errors)
    for root in sorted(errors.keys()):
      errs = errors[root]
      self.log.error('publishing point "%s" failed:', root)
      for idx, err in enumerate(errs):
        try:
          tb = err[2]
          while tb.tb_next is not None: tb = tb.tb_next
          etb = traceback.extract_tb(tb)
          self.log.error('  error %d/%d, file "%s", line %d, in %s:',
                          idx + 1, len(errs), etb[-1][0], etb[-1][1], etb[-1][2])
          self.log.error('    %s.%s',
                         err[0].__module__,
                         traceback.format_exception_only(err[0], err[1])[-1].strip())
          for line in traceback.format_exception(*err):
            for subline in line.rstrip().split('\n'):
              self.log.error('    %s', subline)
          cause = getattr(err[1], 'cause', None)
          if cause is not None:
            # TODO: what about cascading `causes`?... recurse?
            self.log.error('    caused by %s.%s',
                           cause[0].__module__,
                           traceback.format_exception_only(cause[0], cause[1])[-1].strip())
            for line in traceback.format_exception(*cause):
              for subline in line.rstrip().split('\n'):
                self.log.error('      %s', subline)
        except:
          self.log.exception('    failed to display exception:')
    return len(errors)

  #----------------------------------------------------------------------------
  def adjustConfig(self, pubpnt, engconf, engsym):
    ret = aadict()
    ret.update(self.options.engines.get('all', {}).get('defaults', {}))
    ret.update(self.options.engines.get(engsym, {}).get('defaults', {}))
    ret.update(engconf)
    for key, val in self.options.engines.get('all', {}).get('extends', {}):
      ret[key] = asList(ret.get(key)).extend(asList(val))
    for key, val in self.options.engines.get(engsym, {}).get('extends', {}):
      ret[key] = asList(ret.get(key)).extend(asList(val))
    ret.update(self.options.engines.get(engsym, {}).get('overrides', {}))
    ret.update(self.options.engines.get('all', {}).get('overrides', {}))
    return ret

  #----------------------------------------------------------------------------
  def execPublishingPointEngine(self, pubpnt, engconf):
    engine = engconf.engine
    engsym = str2sym(engine)
    handler_options = self.adjustConfig(pubpnt, engconf, engsym)
    # BIG TODO: there is currently a problem here. if the system
    #           configuration disables an engine, via say
    #           'engines.email.overrides.enabled = false' but the
    #           pubpoint general config (not engine-specific) adds
    #           enabled=true, then the option is incorrectly set to
    #           true for context.enabled. note that this is currently
    #           not a problem for `enabled` as that gets checked
    #           early. *BUT* other options are not controlled like
    #           that...
    if not handler_options.get('enabled', True):
      self.log.info('engine "%s" disabled - skipping', engine)
      return
    # stopOnFail = pubobj.config.get('stopOnFail', False)
    try:
      pubname = engconf.get('engine-handler', 'svnpublish.engine.' + engsym + '.publish_' + engsym)
      self.log.info('loading engine "%s" (callable: %s)', engine, pubname)
      handler = symbol(pubname)
      if self.options.dryrun:
        pubname += '_dryrun'
        try:
          handler = symbol(pubname)
        except ImportError:
          self.log.warning('engine "%s" does not support dry-run mode - skipping', engine)
          return
    except ImportError:
      raise api.EngineLoadError(
        'svnpublish engine "%s" does not exist or could not be loaded' % (engine,),
        cause=sys.exc_info())
    context = aadict(pubpnt.config).update(handler_options).update({
      'options'    : handler_options,
      'logger'     : logging.getLogger('svnpublish.' + engine),
      # BEGIN: backward compat,
      'repository' : self.svnrev.svn.repos,
      'revision'   : self.svnrev.rev,
      'revinfo'    : pubpnt.revinfo,
      'root'       : pubpnt.root,
      # END: backward compat,
      'pubpoint'   : pubpnt,
      'svnpub'     : self,
      })
    handler(context)

  #----------------------------------------------------------------------------
  def loadPublishingPoints(self):
    pubpnts = {}
    cfgsrcs = [sources.get(src)(self)
               for src in asList(self.options.configOrder)]
    def parentDirWalk(path):
      while True:
        yield path
        next = os.path.dirname(path)
        if next == path:
          return
        path = next
    overconf = None
    if self.options.overrideConfig is not None:
      overconf = self.options.overrideConfig
      if isstr(overconf):
        overconf = yaml.load(util.getUriContent(overconf, aadict(svnrev=self.svnrev, svndir='')))
      overconf = aadict.d2ar(overconf)
    for change in self.svnrev.changes:
      path = change.path
      if not change.isdir:
        path = os.path.dirname(path)
      self.log.drivel('checking change "%s" for publishing point config', change)
      for root in parentDirWalk(path):
        root = root or '/'
        self.log.noise('checking publishing point "%s" for config', root)
        if len(asList(self.options.publishOnly)) > 0:
          # TODO: add RE flag control...
          # todo: only add the '$' if it does not already end in a '$'...
          if len([e for e in asList(self.options.publishOnly) if re.match(e + '$', root) is not None]) <= 0:
            self.log.debug('publishing point "%s" not in options.publishOnly - skipping', root)
            continue
        conf = None
        for cs in cfgsrcs:
          conf = cs.getConfig(root)
          if conf is not None:
            conf = aadict.d2ar(conf)
            break
        if conf is not None \
           or ( overconf is not None and len(asList(self.options.publishOnly)) > 0 ):
          pubpnts[root] = PublishingPoint(self, root, overconf or conf)
        else:
          self.log.noise('no publishing point config for "%s"', change)
    return sorted(pubpnts.values(), key=operator.attrgetter('root'))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
