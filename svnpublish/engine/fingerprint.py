# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2009/09/13
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
