# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: creates a "fingerprint" of a publishing event
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/13
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import os, json, yaml
from aadict import aadict

from svnpublish.util import ts, evalVars, run

#------------------------------------------------------------------------------

defaultFormat = 'yaml'
defaultTemplates = {
  'yaml': 'revision: %(revision)s\nlast-published: %(publishDate)s\n',
  'json': '{\n  "revision": %(revision)s,\n  "last-published": "%(publishDate)s"\n}\n'
}

#------------------------------------------------------------------------------
def fixate_fingerprint_dryrun(params, srcdir, dstdir):
  return fixate_fingerprint(params, srcdir, dstdir)

#------------------------------------------------------------------------------
def fixate_fingerprint(params, srcdir, dstdir):
  # todo: this is a hack! fetching from params.options in order to
  #       avoid inheriting the 'path' from the 'export' engine...
  fppath = os.path.join(srcdir, params.options.get('path', 'fingerprint'))
  _fingerprint_exec(params, fppath)

#------------------------------------------------------------------------------
def publish_fingerprint_dryrun(params):
  return publish_fingerprint(params)

#------------------------------------------------------------------------------
def publish_fingerprint(params):
  fppath = params.get('path', 'fingerprint')
  _fingerprint_exec(params, fppath)

#------------------------------------------------------------------------------
def _fingerprint_exec(params, fppath):

  fpeval = params.evals and params.evals.toDict() or {}
  fpeval.update(dict(publishDate=ts()))

  tpl = params.get('format', defaultFormat)
  if tpl in defaultTemplates:
    tpl = defaultTemplates[tpl]

  # todo: make this evalVars "better"
  fpdata = evalVars(params, tpl, fpeval)

  if params.dryrun:
    params.logger.info('dryrun: NOT creating fingerprint in "%s":', fppath)
    params.logger.info('  %s', repr(fpdata))
    return

  params.logger.debug('creating fingerprint in "%s"', fppath)

  env = aadict(params.env or {})

  run(params.prefix, 'mkdir', '--parents', os.path.dirname(fppath), env=env)

  # todo: this will overwrite fppath if it exists... should i create an option
  #      'no-overwrite'? note that this gets a little more complicated when
  #      running in remote export mode...

  run(params.prefix, 'tee', fppath, env=env, input=fpdata)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
