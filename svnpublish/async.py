# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/11/05
# copy: (C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
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

import sys, os, argparse, logging, signal, threading, pickle, subprocess
import pwd, grp
from aadict import aadict

from . import framework
from .util import SvnpublishLogFormatter
from .i18n import _

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Daemon(object):

  def __init__(self, svcdir, period=300, *args, **kw):
    super(Daemon, self).__init__(*args, **kw)
    self.svcdir  = svcdir
    self.taskdir = os.path.abspath(os.path.join(svcdir, 'tasks'))
    self.cond    = threading.Condition()
    if not os.path.exists(self.taskdir):
      os.makedirs(self.taskdir)
    if not os.path.isdir(self.taskdir):
      raise ValueError('expected "%s" to be a directory' % (self.taskdir,))
    self.period  = period
    self.stopreq = False

  #----------------------------------------------------------------------------
  def start(self):
    while True:
      task = self.getNextTask()
      if task is None:
        return
      self.handleTask(task)

  #----------------------------------------------------------------------------
  def stop(self):
    with self.cond:
      self.stopreq = True
      self.cond.notify()

  #----------------------------------------------------------------------------
  def scan(self):
    with self.cond:
      self.cond.notify()

  #----------------------------------------------------------------------------
  def getNextTask(self):
    with self.cond:
      while True:
        if self.stopreq:
          log.info('stop requested - scanning terminated.')
          return None
        log.debug('scanning for tasks...')
        for fname in sorted(os.listdir(self.taskdir)):
          if fname.startswith('task.') \
              and fname.endswith('.pkl') \
              and os.path.isfile(os.path.join(self.taskdir, fname)):
            log.info('found task: %s', fname)
            return fname
        log.debug('no pending tasks found - waiting')
        self.cond.wait(self.period)

  #----------------------------------------------------------------------------
  def handleTask(self, taskid):
    log.info('handling task: %s', taskid)
    fname = os.path.join(self.taskdir, taskid)
    dname = os.path.join(self.taskdir, 'processing-' + taskid)
    with open(fname, 'rb') as fp:
      task = pickle.load(fp)
    os.rename(fname, dname)
    try:
      self.launchTask(aadict(task))
      os.unlink(dname)
      log.info('task complete: %s', taskid)
    except Exception:
      log.exception('failed during handling of task %s', taskid)
      # todo: ideally, this would email the admins...
      raise

  #----------------------------------------------------------------------------
  def launchTask(self, task):
    # task.id, task.env, task.cwd, task.uid, task.gid, task.cmd
    # TODO: use uid/gid ?...
    # TODO: add a 'paranoid' mode where only svnpublish from the same
    #       distribution is allowed...
    log.debug('executing task %s: %r', task.id, task.cmd)
    subprocess.check_call(
      task.cmd,
      cwd    = task.cwd,
      env    = aadict(task.env or dict()).update(SVNPUBLISHD_ASYNC='0'),
      stdout = sys.stdout,
      stderr = sys.stderr,
      )
    log.debug('done executing task %s', task.id)

#------------------------------------------------------------------------------
def initServiceDir(options):
  svcdir    = os.path.abspath(options.svcdir)
  tskdir    = os.path.join(svcdir, 'tasks')
  logsvcdir = os.path.join(svcdir, 'log')
  varlogdir = options.logdir or os.path.join(svcdir, 'log', 'logs')
  for dname, dpath in (
    ('service',      svcdir),
    ('task',         tskdir),
    ('log service',  logsvcdir),
    ('log output',   varlogdir),
    ):
    if not os.path.exists(dpath):
      log.info('creating %s directory: "%s"...', dname, dpath)
      os.makedirs(dpath)
    if not os.path.isdir(dpath):
      log.error('%s directory "%s" is not a directory', dname, dpath)
      return 10
  runfile = os.path.join(svcdir, 'run')
  if not os.path.exists(runfile):
    downfile = os.path.join(svcdir, 'down')
    log.info('creating "service down" trigger: "%s"...', downfile)
    with open(downfile, 'wb') as fp:
      pass
    log.info('creating service script: "%s"...', runfile)
    with open(runfile, 'wb') as fp:
      spd = os.path.abspath(sys.argv[0]) if len(sys.argv) > 0 else ''
      if not spd.endswith('/svnpublishd'):
        spd = 'svnpublishd'
      fp.write('''\
#!/bin/sh
exec \\
setuidgid "{uid}" \\
"{spd}" \\
  --service-dir "{svcdir}" \\
  --period 300 \\
  --log-level info \\
2>&1
'''.format(uid=options.owner.split(':')[0], spd=spd, svcdir=svcdir))
    os.chmod(runfile, 0755)
  logrunfile = os.path.join(logsvcdir, 'run')
  if not os.path.exists(logrunfile):
    log.info('creating log service script: "%s"...', logrunfile)
    with open(logrunfile, 'wb') as fp:
      fp.write('''\
#!/bin/sh
## the following keeps up to 10MB of timestamped logs
exec multilog t s1048576 n10 {varlogdir}
'''.format(varlogdir=varlogdir))
    os.chmod(logrunfile, 0755)
  log.info('setting user:group of task directory: "%s"...', tskdir)
  uid = pwd.getpwnam(options.owner.split(':')[0]).pw_uid
  gid = grp.getgrnam(options.owner.split(':')[1]).gr_gid
  os.chown(tskdir, uid, gid)

#------------------------------------------------------------------------------
def main(args=None):

  cli = argparse.ArgumentParser(
    description = _('Asynchronous svnpublish daemon')
    )

  cli.add_argument(
    _('-V'), _('--version'),
    dest='version', default=False, action='store_true',
    help=_('output current svnpublish version and exit'))

  cli.add_argument(
    _('-l'), _('--log-level'), metavar=_('LEVEL'),
    dest='loglvl', default='warning', action='store',
    help=_('sets the verbosity of the logging subsystem, which is'
           ' sent to STDERR; it must be an integer or one of the'
           ' "logging" module defined levels such as "debug", "info",'
           ' "warning", "error", "critical" (default: %(default)s)'))

  cli.add_argument(
    _('-d'), _('--service-dir'), metavar=_('DIRECTORY'),
    dest='svcdir', default=None, action='store',
    help=_('sets the running directory for the svnpublishd daemon --'
           ' this must match the directory specified in the'
           ' svnpublish "serviceDir" option (default: %(default)s)'))

  cli.add_argument(
    _('-p'), _('--period'), metavar=_('SECONDS'),
    dest='period', default=300, action='store', type=int,
    help=_('sets the interval (in seconds) that svnpublishd should'
           ' check for pending tasks; note that this is a paranoia'
           ' setting, as during normal operation, svnpublishd will'
           ' be notified as soon as a new task is available'
           ' (default: %(default)s)'))

  cli.add_argument(
    _('--init-service'),
    dest='initservice', default=False, action='store_true',
    help=_('initializes the service directory with all the standard'
           ' directories, scripts, and logging options for the'
           ' specified "--service-dir" and "--user" options'))

  cli.add_argument(
    _('--user'), metavar=_('USER:GROUP'),
    dest='owner', default=None, action='store',
    help=_('sets the user and group that the svnpublish script'
           ' will be run as -- this is typically the owner of the'
           ' subversion repository (only used by "--init-service",'
           ' and will not overwrite any existing values)'))

  cli.add_argument(
    _('-L'), _('--log-dir'), metavar=_('DIRECTORY'),
    dest='logdir', default=None, action='store',
    help=_('sets the directory that logs will be sent to using'
           ' daemontools\' "multilog" process (only used by'
           ' "--init-service", and will not overwrite any existing'
           ' values)'))

  options = cli.parse_args(args)

  if options.version:
    print framework.version
    return 0

  # configure the logging
  logger  = logging.getLogger()
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(SvnpublishLogFormatter())
  logger.addHandler(handler)
  level = options.loglvl
  if isinstance(getattr(logging, level.upper()), int):
    level = getattr(logging, level.upper())
  logger.setLevel(int(level))

  if not options.svcdir:
    return cli.error('option "--service-dir" is required')

  if options.initservice:
    if not options.owner:
      return cli.error('"--init-service" requires "--user" to be specified')
    logger.setLevel(0)
    return initServiceDir(options)

  log.info('svnpublishd v%s initializing (pid=%d, uid=%d)',
           framework.version, os.getpid(), os.getuid())
  daemon = Daemon(options.svcdir, period=options.period)
  registerSignalHandlers(daemon)
  daemon.start()

#------------------------------------------------------------------------------
def registerSignalHandlers(daemon):
  def term(signo=None, frame=None):
    log.info('received SIGTERM -- requesting clean exit')
    daemon.stop()
  def hup(signo=None, frame=None):
    log.debug('received SIGHUP -- requesting task scan')
    daemon.scan()
  log.debug('registering SIGHUP signal handler')
  signal.signal(signal.SIGTERM, term)
  signal.signal(signal.SIGHUP, hup)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
