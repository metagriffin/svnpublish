# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# desc: svnpublish logging utilities
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/04
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

from __future__ import absolute_import
import logging, new

#------------------------------------------------------------------------------
# adding "noise" and "drivel" to the logging levels...

logging.NOISE  = 3
logging.DRIVEL = 7
logging.addLevelName(logging.NOISE,  'NOISE')
logging.addLevelName(logging.DRIVEL, 'DRIVEL')

def addMethodToClass(func, kls, name=None):
  method = new.instancemethod(func, None, kls)
  if not name:
    name = func.__name__
  setattr(kls, name, method)
def noise(self, msg, *args, **kwargs): self.log(logging.NOISE, msg, *args, **kwargs)
def drivel(self, msg, *args, **kwargs): self.log(logging.DRIVEL, msg, *args, **kwargs)
addMethodToClass(noise, logging.Logger)
addMethodToClass(drivel, logging.Logger)

#------------------------------------------------------------------------------
class SvnpublishLogFormatter(logging.Formatter):
  # todo: what about handling other log levels?
  levelString = {
    logging.NOISE      : '[  ] NOISE   ',
    logging.DRIVEL     : '[  ] DRIVEL  ',
    logging.DEBUG      : '[  ] DEBUG   ',
    logging.INFO       : '[--] INFO    ',
    logging.WARNING    : '[++] WARNING ',
    logging.ERROR      : '[**] ERROR   ',
    logging.CRITICAL   : '[**] CRITICAL',
    }
  def format(self, record):
    msg = record.getMessage()
    pfx = '%s|%s: ' % (self.levelString[record.levelno], record.name)
    return pfx + ('\n' + pfx).join(msg.split('\n'))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
