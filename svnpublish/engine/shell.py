# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: executes a shell command for either 'fixate' or 'finalize' engines
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/13
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import sys
from aadict import aadict

from svnpublish.util import ts, evalVars, run, runchk

#------------------------------------------------------------------------------
def fixate_shell_dryrun(params, srcdir, dstdir):
  return fixate_shell(params, srcdir, dstdir)

#------------------------------------------------------------------------------
def fixate_shell(params, srcdir, dstdir):
  if params.dryrun:
    params.logger.info('dryrun: NOT running fixate shell command "%s"', params.command)
    return

  # TODO: this is also in fingerprint.py, and down below... DRY!
  shell_eval = aadict(params.evals or {}).update({
    'publishDate' : ts(),
    })

  shell_env = aadict(params.env or {}).update({
    'SVNPUBLISH_STAGE'  : srcdir,
    'SVNPUBLISH_TARGET' : dstdir,
    })

  params.logger.debug('running fixate shell command "%s"', params.command)

  out = run(params.prefix or ['/bin/sh', '-c'],
            evalVars(params, params.command, shell_eval),
            env=shell_env)

  if out:
    params.logger.info(out)

#------------------------------------------------------------------------------
def finalize_shell_dryrun(params, dstdir):
  return finalize_shell(params, dstdir)

#------------------------------------------------------------------------------
def finalize_shell(params, dstdir):
  if params.dryrun:
    params.logger.info('dryrun: NOT running finalize shell command "%s"', params.command)
    return

  # TODO: this is also in fingerprint.py, and up above... DRY!
  shell_eval = aadict(params.evals or {}).update({
    'publishDate' : ts(),
    })

  # TODO: make this work in remote-mode by setting all the environment
  #      variables in-line...

  shell_env = aadict(params.env or {}).update({
    'SVNPUBLISH_TARGET' : dstdir,
    })

  params.logger.debug('running finalize shell command "%s"', params.command)

  out = run(params.prefix or ['/bin/sh', '-c'],
            evalVars(params, params.command, shell_eval),
            env=shell_env)

  if out:
    params.logger.info(out)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
