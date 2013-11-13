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

#------------------------------------------------------------------------------
# TODO: why not pass *ALL* config variables through a generic evalVars()?
#       the easiest way to do that would be to convert the config object to
#       a class...
#------------------------------------------------------------------------------

import sys, os, os.path, re, hashlib, logging
from aadict import aadict
from asset import isstr, symbol

from svnpublish.util import asList, str2sym, evalVars, run, runchk

#------------------------------------------------------------------------------
def evalEnv(params, prefix=None, envSet=None, envMod=None, evals=None, env=None):
  ret = {}
  if envSet is not None:
    ret = envSet
  else:
    for k, v in re.findall('^([^=]+)=([^\n]*)\n', run(prefix, '/usr/bin/env', env=env), re.M):
      ret[k] = v
  if evals is not None:
    ret.update(evals)
  if envMod is not None:
    for k, v in envMod.items():
      ret[k] = evalVars(params, v, ret)
  if env is not None:
    ret.update(env)
  return ret

#------------------------------------------------------------------------------
def publish_export_dryrun(params):
  return publish_export(params)

#------------------------------------------------------------------------------
def publish_export(params):
  '''
  Configurable parameters:

  :Parameters:

  incremental : bool, optional, default: false
    todo

  path : str

  symlink : str, optional, default: none
    todo

  symlink-target : str, optional, default: none
    todo

  keychain : str, optional, default: none
    todo

  remote : str, optional, default: none
    todo

  fixate : list(engine), optional, default: none
    todo

  fixate-env[+] : dict, optional, default: none
    todo

  fixate-host : str, optional, default: none
    todo

  fixate-host-env[+] : dict, optional, default: none
    todo

  finalize : list(engine), optional, default: none
    todo

  finalize-env[+] : dict, optional, default: none
    todo

  archive : todo, optional, default: none
    todo

  TODO: add docs...
  '''

  if params.get('incremental', False):
    # TODO: implement
    raise NotImplementedError()

  # TODO: error trap all this and recover...

  # steps:
  #   - create export structure
  #   - fixate structure
  #   - create distribution tarball
  #   - transfer tarball to remote host (or locally if not remote)
  #   - extract tarball
  #   - host-specific fixate installation
  #   - create symlinks, etc
  #   - finalize installation

  tarball = 'svnpublish.%s.%s' \
            % (hashlib.sha1(str(repr(os.uname()))).hexdigest(), str(os.getpid()))
  tpath = '/tmp/' + tarball

  params.logger.info('tarball "%s"', tarball)

  runchk(params, 'rm', '--force', '--recursive', tpath)

  runchk(params,
         'svn', 'export',
         '--quiet', '--no-auth-cache', '--non-interactive', '--ignore-externals',
         '--revision', params.revision,
         'file://' + os.path.abspath(params.repository) + '/' + params.root,
         tpath)

  # TODO: this should probably be done on a per-host basis... that way
  #      the fixate (and not only the fixate-host and finalize) can be
  #      host-specific...
  path = evalVars(params, params['path'], None)
  run_engines(params, 'fixate', 'fixate', args=[tpath, path])

  runchk(params,
         'tar', '--create', '--gzip', '--file=' + tpath + '.tgz',
         '--directory=' + tpath,
         '.')

  keychain = params.get('keychain')
  keyenv = None

  if keychain is not None:
    output = runchk(params,
                    '/usr/bin/keychain', '--nogui', '--noask', '--quick', '--quiet',
                    '--timeout', '1',
                    '--dir', keychain, '--eval')
    if output is not None:
      keyenv = {}
      for s in output.split('\n'):
        m = re.match('([^=]+)=([^;]+);', s)
        if m is None:
          continue
        keyenv[m.group(1)] = m.group(2)

  runchk(params, 'rm', '--force', '--recursive', tpath)

  hosts = params.get('remote')

  if hosts is None:
    run_export_install(params, tarball)

  else:
    for host in asList(hosts):
      params.logger.info('installing on remote host "%s"', host)
      runchk(params,
             'scp', tpath + '.tgz', host + ':' + tpath + '.tgz',
             env=keyenv)
      evals = {
        'host': host.find('@') >= 0 and host[host.index('@') + 1:] or host,
        }
      run_export_install(params, tarball,
                         prefix=['ssh', host], evals=evals, env=keyenv)
      runchk(params,
             'ssh', host,
             'rm', '--force', tpath + '.tgz',
             env=keyenv)

  runchk(params, 'rm', '--force', tpath + '.tgz')

#------------------------------------------------------------------------------
def run_engines(params, paramkey, engtype, args=None,
                prefix=None, evals=None, env=None):
  if params.get(paramkey) is None:
    return

  if args is None:
    args = []

  engines = asList(params.get(paramkey))

  engine_env = evalEnv(params, prefix,
                       params.get(paramkey + '-env'), params.get(paramkey + '-env+'),
                       evals, env)

  for engcfg in engines:
    if isstr(engcfg):
      engcfg = aadict(engine='shell', command=engcfg)
    engine   = engcfg.engine
    engsafe  = str2sym(engine)
    funcname = engcfg.get('engine-handler', 'svnpublish.engine.%s.%s_%s' % (engsafe, engtype, engsafe))
    params.logger.info('loading %s engine "%s" (%s)', engtype, engine, funcname)
    handler = symbol(funcname)
    if params.dryrun:
      funcname += '_dryrun'
      try:
        handler = symbol(funcname + '_dryrun')
      except ImportError:
        params.logger.debug('engine "%s" does not support dry-run mode - skipping', engine)
        continue
    engine_params = aadict(params).update(engcfg).update({
      'options' : engcfg,
      'logger'  : logging.getLogger('.'.join((params.logger.name, engtype, engine))),
      'prefix'  : prefix,
      'env'     : engine_env,
      'evals'   : evals,
      })
    handler(engine_params, *args)

#------------------------------------------------------------------------------
def run_export_install(params, tarball,
                       prefix=None, evals=None, env=None):

  tpath  = '/tmp/' + tarball
  tpathi = tpath + '-install'
  path   = evalVars(params, params['path'], evals)

  runchk(params, prefix, 'rm', '--force', '--recursive', tpathi,
         env=env)

  runchk(params, prefix, 'mkdir', '--parents', tpathi,
         env=env)

  runchk(params, prefix, 'tar', '--extract', '--gunzip',
         '--file=' + tpath + '.tgz', '--directory=' + tpathi,
         env=env)

  runchk(params, prefix, 'mkdir', '--parents', path,
         env=env)

  run_engines(params, 'fixate-host', 'fixate', args=[tpathi, path],
              prefix=prefix, evals=evals, env=env)

  if params.get('archive') is None:
    runchk(params, prefix, 'mv', '--force', path, path + '.old',
           env=env)
  else:
    keeppath = evalVars(params, params.archive, evals, {'path': path})
    runchk(params, prefix, 'rm', '--force', keeppath,
           env=env)
    runchk(params, prefix, 'mkdir', '--parents', os.path.dirname(keeppath),
           env=env)
    runchk(params, prefix, 'mv', '--force', path, keeppath,
           env=env)

  runchk(params, prefix, 'mv', '--force', tpathi, path,
         env=env)

  if params.get('symlink') is not None:

    symtgt = evalVars(params, params.get('symlink-target'), evals)
    if symtgt is None:
      symtgt = path

    runchk(params, prefix, 'rm', '--force', params.get('symlink'),
           env=env)

    runchk(params, prefix, 'ln', '--symbolic', symtgt, params.get('symlink'),
           env=env)

  run_engines(params, 'finalize', 'finalize', args=[path,],
              prefix=prefix, evals=evals, env=env)

  if params.get('archive') is None:
    runchk(params, prefix, 'rm', '--force', '--recursive', path + '.old',
           env=env)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
