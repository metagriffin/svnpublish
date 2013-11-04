# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: creates a "genshic" of a publishing event
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/13
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
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
