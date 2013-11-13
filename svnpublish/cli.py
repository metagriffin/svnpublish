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

'''
The svnpublish.cli module provides the command line interface to the
svnpublish engine.
'''

import sys, os, argparse, six, logging, yaml, traceback, pipes, pickle
import time, uuid, subprocess, pkg_resources
from aadict import aadict

from . import framework, api, revinfo, subversion, util
from .util import SvnpublishLogFormatter, asList
from .i18n import _

#------------------------------------------------------------------------------
def main(args=None):

  cli = argparse.ArgumentParser(
    description = _('Powerful automation from a subversion repository.'),
    )

  cli.add_argument(
    _('-V'), _('--version'),
    dest='version', default=False, action='store_true',
    help=_('output current svnpublish version and exit'))

  cli.add_argument(
    _('--init-options'),
    dest='initOptions', default=False, action='store_true',
    help=_('generates a blank options file, with all options documented'
           ' and default values specified -- this is the perfect way to'
           ' start configuring svnpublish: save the output to your'
           ' preferred configuration location (e.g.'
           ' /etc/svnpublish/options.yaml) and edit'))

  cli.add_argument(
    _('-v'), _('--verbose'),
    dest='verbose', default=0, action='count',
    help=_('enable verbose output to STDERR, mostly for diagnotic'
           ' purposes (multiple invocations increase verbosity).'
           ' IMPORTANT: if invoked at least once, errors will NOT'
           ' be emailed to the admin (to increase that verbosity,'
           ' use "--log-level")'))

  cli.add_argument(
    _('-0'), _('-n'), _('--dryrun'),
    dest='dryrun', default=None, action='store_true',
    help=_('enable "dry-run" mode: no actions will actually be'
           ' executed; they will only be reported'))

  cli.add_argument(
    _('-l'), _('--log-level'), metavar=_('LEVEL'),
    dest='logLevel', default='warning', action='store',
    help=_('sets the verbosity of the logging subsystem, which on'
           ' error is sent to the administrators. it must be set to'
           ' one of "noise", "drivel", "debug", "info", "warning",'
           ' "error", "critical" (in decreasing order of verbosity),'
           ' and by default set to: %(default)s'))

  cli.add_argument(
    _('-o'), _('--options'), metavar=_('FILENAME'),
    dest='options', default=None, action='store',
    help=_('main svnpublish options file'))

  cli.add_argument(
    _('-a'), _('--async'),
    dest='async', default=False, action='store_true',
    help=_('run the svnpublish tasks in asynchronous mode; note that'
           ' svnpublishd must be running and that the "serviceDir"'
           ' option must be correctly set'))

  cli.add_argument(
    _('-y'), _('--options-yaml'), metavar=_('YAML'),
    dest='optionsYaml', default=None, action='store',
    help=_('overrides the options specified via "--options" as a YAML'
           ' overlay e.g.: "--options-yaml \'{admin: foo@example.com}"\''))

  cli.add_argument(
    _('-p'), _('--publish'), metavar=_('PATH'),
    dest='publish', default=None, action='store',
    help=_('publish the specified PATH only -- note that if the PATH'
           ' (and sub-paths) does not have any changed entries, the'
           ' PATH (but only the PATH, no sub-paths) will be marked as'
           ' "modified". if sub-paths should be marked as well, use'
           ' "--as-modified". note also that if there is no configuration'
           ' for the specified publishing point, then no action will be'
           ' taken -- in that case use "--config" to force a configuration.'))

  cli.add_argument(
    _('-c'), _('--config'), metavar=_('FILENAME'),
    dest='overrideConfig', default=None, action='store',
    help=_('overrides options.overrideConfig'))

  cli.add_argument(
    _('-m'),  _('--as-modified'), metavar=_('ROOT'),
    dest='modified', default=None, action='store',
    help=_('mark all entries in the specified directory (can be "/"'
           ' to match all entries) as "modified" and all other entries'
           ' as being unchanged.'))

  cli.add_argument(
    'repos', metavar=_('REPOSITORY'), nargs='?',
    help=_('path to the subversion repository'))

  cli.add_argument(
    'rev', metavar=_('REVISION'), nargs='?',
    help=_('revision to publish'))

  #------------------------------------------------------------------------------

  options = cli.parse_args(args)

  if options.version:
    print framework.version
    return 0

  if options.initOptions:
    output = framework.defaultOptions.split('\n')
    for idx, line in enumerate(output):
      if len(line) <= 0 or line[0] == '#':
        continue
      output[idx] = '# ' + line
    sys.stdout.write('\n'.join(output))
    return 0

  if options.repos is None or options.rev is None:
    cli.error(_('REPOSITORY and/or REVISION not specified'))

  exitcode = 0

  # setup logging - plan:
  #   if verbose, send as defined to stderr
  #   if not verbose:
  #     with no errors:
  #       send email if any messages at desired level to admin
  #     with errors:
  #       send email if any messages at desired level to admin
  #       send critical to stderr and exit

  # configure the root logger so all logging will default to that
  logger = logging.getLogger()
  errlog = six.StringIO()
  notifyAdminBuffer = six.StringIO()

  if options.verbose > 0:
    # setup immediate logging to stderr
    handler = logging.StreamHandler()
    handler.setFormatter(SvnpublishLogFormatter())
    logger.addHandler(handler)
    if options.verbose == 1:   logger.setLevel(logging.INFO)
    elif options.verbose == 2: logger.setLevel(logging.DEBUG)
    elif options.verbose == 3: logger.setLevel(logging.DRIVEL)
    elif options.verbose == 4: logger.setLevel(logging.NOISE)
    else:                      logger.setLevel(logging.NOTSET)

  else:
    # setup ERR+ to buffer for later output in the case of an error
    handler = logging.StreamHandler(errlog)
    handler.setFormatter(SvnpublishLogFormatter())
    handler.setLevel(logging.CRITICAL)
    logger.addHandler(handler)
    # setup normal log handler for email to admins
    handler = logging.StreamHandler(notifyAdminBuffer)
    handler.setFormatter(SvnpublishLogFormatter())
    loglevels = {
      'noise':    logging.NOISE,
      'drivel':   logging.DRIVEL,
      'debug':    logging.DEBUG,
      'info':     logging.INFO,
      'warn':     logging.WARNING,
      'warning':  logging.WARNING,
      'error':    logging.ERROR,
      'fatal':    logging.CRITICAL,
      'critical': logging.CRITICAL,
      }
    if not loglevels.has_key(options.logLevel):
      print >>sys.stderr, '[**] ERROR: invalid log level "%s", using "warning"' % (options.logLevel,)
      exitcode |= 1 << 0
    level = loglevels.get(options.logLevel, logging.WARN)
    handler.setLevel(level)
    logger.addHandler(handler)
    if logger.getEffectiveLevel() > level:
      logger.setLevel(level)

  # switch to svnpublish logger for the remainder of main()
  logger = logging.getLogger('svnpublish')

  #----------------------------------------------------------------------------
  # setup the svnpublish options

  logger.info('svnpublish v%s initializing (pid=%d, uid=%d)',
              framework.version, os.getpid(), os.getuid())

  runoptions = aadict.d2ar(yaml.load(framework.defaultOptions))

  if options.options is not None:
    logger.info('loading svnpublish configuration from "%s"...' % options.options)
    cliopts = aadict.d2ar(yaml.load(open(options.options, 'rb').read()))
    runoptions = util.mergeOptions(runoptions, cliopts)

  if options.optionsYaml is not None:
    logger.info('loading command-line options structure...')
    cliopts = aadict.d2ar(yaml.load(options.optionsYaml))
    runoptions = util.mergeOptions(runoptions, cliopts)

  if options.dryrun is not None and options.dryrun:
    runoptions.dryrun = True

  if options.overrideConfig:
    runoptions.overrideConfig = options.overrideConfig

  #----------------------------------------------------------------------------
  # check for asynchronous mode

  if options.async and runoptions.serviceDir \
      and os.environ.get('SVNPUBLISHD_ASYNC') != '0':
    task = 'task.{rev}.{ts}.{uuid}.pkl'.format(
      rev=options.rev, ts=int(time.time()), uuid=str(uuid.uuid4()))
    logger.info('creating asynchronous task: %s', task)
    fname = os.path.join(runoptions.serviceDir, 'tasks', task)
    with open(fname, 'wb') as fp:
      pickle.dump(dict(
        id  = task,
        env = dict(os.environ),
        cwd = os.getcwd(),
        uid = os.getuid(),
        gid = os.getgid(),
        cmd = list(args or sys.argv),
        ), fp)
    subprocess.check_call(['sudo', 'svc', '-h', runoptions.serviceDir])
    return exitcode

  #----------------------------------------------------------------------------
  # create the subversion interface

  svnrev = revinfo.RevisionInfo(subversion.Subversion(options.repos), options.rev)

  if options.publish is not None:
    logger.info('marking entry "%s" as modified' % (options.publish,))
    svnrev.markUpdated(options.publish)

  if options.modified is not None:
    logger.info('marking all content in "%s" as modified' % (options.modified,))
    svnrev.markAllUpdated(options.modified, overlay=True)

  #----------------------------------------------------------------------------
  # create a special ConfigSource if "--publish" is used...

  if options.publish is not None:
    class ConfigSourceCliPublish(api.ConfigSource):
      def getConfig(self, root):
        if os.path.normpath(options.publish) != os.path.normpath(root):
          return None
        # this is enough to tell the framework to engage publishing point
        # processing -- at that point, the *actual* config from "--config"
        # should take over.
        return dict()
    framework.sources.register('cli-publish', ConfigSourceCliPublish)
    runoptions.configOrder.append('cli-publish')

  #----------------------------------------------------------------------------
  # create the managers and framework and hand over control

  svnpub = None
  errors = 0

  try:
    svnpub   = framework.Framework(runoptions, svnrev=svnrev)
    errors   = svnpub.run()
    exitcode |= errors << 4

  except Exception:
    et, ev = sys.exc_info()[:2]
    logger.critical('failed to run svnpublish framework:')
    logger.critical('  %s.%s', et.__module__, traceback.format_exception_only(et, ev)[-1].strip())
    logger.error(traceback.format_exc().strip())
    exitcode |= 1 << 2

  #------------------------------------------------------------------------------
  # display and handle any errors

  adat = notifyAdminBuffer.getvalue()
  if len(adat) > 0:
    try:
      eml = svnpub.genemail.newEmail('error', provider=svnpub.talchemy['framework'])
      eml.setHeader('To', ', '.join(asList(runoptions.admin)))
      eml['options']      = runoptions
      eml['errorCount']   = errors
      eml['messages']     = adat
      eml['messageCount'] = len(adat.split('\n')) - 1
      eml['command']      = ' '.join(pipes.quote(e) for e in sys.argv)
      eml.send()
    except Exception:
      et, ev = sys.exc_info()[:2]
      logger.error('failed to send error notice to admins:')
      logger.error('  %s.%s', et.__module__, traceback.format_exception_only(et, ev)[-1].strip())
      logger.error(traceback.format_exc().strip())
      sys.stderr.write(notifyAdminBuffer.getvalue())
      exitcode |= 1 << 3

  if exitcode == 0:
    return 0

  edat = errlog.getvalue()
  if len(edat) > 0:
    sys.stderr.write(edat)

  return exitcode

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
