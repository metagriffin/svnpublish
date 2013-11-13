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
