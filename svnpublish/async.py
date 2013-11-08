# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/11/05
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import sys, os, argparse, logging, signal, threading, pickle, subprocess
from aadict import aadict

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
    dname = os.path.join(self.taskdir, 'work-' + taskid)
    with open(fname, 'rb') as fp:
      task = pickle.load(fp)
    os.rename(fname, dname)
    try:
      self.launchTask(aadict(task))
      os.unlink(dname)
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
def main(args=None):

  cli = argparse.ArgumentParser(
    description = _('Asynchronous svnpublish daemon')
    )

  cli.add_argument(
    _('-l'), _('--log-level'), metavar=_('LEVEL'),
    dest='logLevel', default='warning', action='store',
    help=_('sets the verbosity of the logging subsystem, which is'
           ' sent to STDERR; it must be an integer or one of the'
           ' "logging" module defined levels such as "debug", "info",'
           ' "warning", "error", "critical" (default: %(default)s)'))

  cli.add_argument(
    _('-d'), _('--service-dir'), metavar=_('DIRECTORY'),
    dest='svcdir', default=os.getcwd(), action='store',
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

  options = cli.parse_args(args)

  # configure the logging
  logger  = logging.getLogger()
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(SvnpublishLogFormatter())
  logger.addHandler(handler)
  level = options.logLevel
  if isinstance(getattr(logging, level.upper()), int):
    level = getattr(logging, level.upper())
  logger.setLevel(int(level))

  log.info('svnpublishd initializing (pid=%d, uid=%d)', os.getpid(), os.getuid())
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