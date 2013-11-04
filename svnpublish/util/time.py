# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/10/16
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

from __future__ import absolute_import
import time

#------------------------------------------------------------------------------
def now():
  return time.time()

#------------------------------------------------------------------------------
def ts(t=None):
  'returns a timestamp string in the format "YYYYMMDDTHHMMSSZ".'
  if t is None:
    t = time.time()
  return time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(t))

#------------------------------------------------------------------------------
def tsl(t=None):
  'returns a "long" version of ts(), ie in the format "YYYY-MM-DDTHH:MM:SSZ".'
  if t is None:
    t = time.time()
  return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))

#------------------------------------------------------------------------------
def ts_iso(t=None):
  '''
  returns the same as datetime.datetime.utcfromtimestamp(t).isoformat(),
  except it forces the timezone offset to be displayed (as +00:00).
  '''
  if t is None:
    t = time.time()
  return time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(t))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
