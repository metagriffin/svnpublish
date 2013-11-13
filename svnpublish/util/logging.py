# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2009/09/04
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
