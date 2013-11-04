# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/10/16
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

from __future__ import absolute_import
import os
from aadict import aadict

from .time import ts

#------------------------------------------------------------------------------
def evalVars(config, path, evals=None, evals2=None):
  if path is None:
    return path
  if path.find('%') < 0:
    return path
  lookup = dict(
    revision    = config.revision,
    repository  = config.repository,
    publishRoot = config.root,
    timestamp   = ts(),
    pid         = str(os.getpid()),
    )
  if evals is not None:
    lookup.update(evals)
  if evals2 is not None:
    lookup.update(evals2)
  return path % lookup

#------------------------------------------------------------------------------
def mergeOptions(base, update):
  if not hasattr(base, 'items') or not hasattr(base, 'keys') \
     or not hasattr(update, 'items') or not hasattr(update, 'keys'):
    return update
  ret = aadict()
  for key in base.keys():
    if key not in update:
      ret[key] = base[key]
    else:
      val = update[key]
      if val is not None:
        ret[key] = mergeOptions(base[key], update[key])
  for key in [k for k in update.keys() if k not in base]:
    val = update[key]
    if val is not None:
      ret[key] = val
    elif key in ret:
      del ret[key]
  return ret

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
