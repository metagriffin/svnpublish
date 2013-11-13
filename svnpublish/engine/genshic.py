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

import sys, re, genshi.template
from aadict import aadict

from svnpublish.util import asList, ts, run, runchk

#------------------------------------------------------------------------------
def fixate_genshic_dryrun(params, srcdir, dstdir):
  return fixate_genshic(params, srcdir, dstdir)

#------------------------------------------------------------------------------
def fixate_genshic(params, srcdir, dstdir):
  '''
  Configurable parameters:

  :Parameters:

  list : list, optional
  find : dict, optional
    name : str, optional
    iname : str, optional
    type : str, optional
  params : dict, optional
  prefix : str, optional

  '''

  targets = None
  if params.list is not None:
    params.logger.debug('using configuration target list')
    targets = asList(params.list, None)
  else:
    if params.get('find') is not None:
      params.logger.debug('using "find" output target list')
      cmd = ['find',]
      if params.find.get('dir') is not None:
        cmd.append(os.path.join(srcdir, params.find.dir))
      else:
        cmd.append(srcdir)
      for cfg in ['name', 'iname', 'type']:
        if params.find.get(cfg) is not None:
          cmd.extend(['-' + cfg, params.find.get(cfg)])
      cmd.extend(['-type', 'f'])
      targets = runchk(params,
                       params.prefix,
                       env=aadict(params.env or {}),
                       *cmd)
      if targets is not None:
        targets = targets.split('\n')

  if targets is not None:
    targets = [t for t in targets if len(t) > 0]
  if targets is None or len(targets) <= 0:
    params.logger.info('no targets - done')
    return

  gstLoader = genshi.template.TemplateLoader(
    '.', auto_reload=True, variable_lookup='lenient')

  tplVars = aadict(params.params or {
    'revinfo'     : params.revinfo,
    'params'      : params,
    'publishDate' : ts(),
    }).update(params.get('params-item+') or {})

  genshic_env = aadict(params.env or {})

  # TODO: i *NEED* to create some way of generalizing this template handling
  #      so that all template rendering (eg fingerprint.py, email.py) all
  #      share the same code...

  for tgt in targets:
    # TODO: make this configurable
    tgtc = re.sub('\.gst$', '', tgt)

    params.logger.info('genshic "%s" to "%s"', tgt, tgtc)
    if params.dryrun:
      continue

    # todo: i *should* be using the gstLoader from above, but...
    # TemplateLoader's cache does not properly include directory, see:
    #   http://genshi.edgewall.org/ticket/240
    #   http://genshi.edgewall.org/ticket/421
    # work-around, create a new TemplateLoader...
    gstLoader = genshi.template.TemplateLoader(
      '.', auto_reload=True, variable_lookup='lenient')

    # todo: implement rendering type guessing a la gstc.py
    tpl = gstLoader.load(tgt)
    out = tpl.generate(**tplVars)\
          .render(params.get('render-type','html'),
                  doctype=params.get('render-doctype','html'))

    run(params.prefix, 'tee', tgtc, env=genshic_env, input=out)

    if params.get('delete-template', False):
      run(params.prefix, 'rm', '--force', tgt, env=genshic_env)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
