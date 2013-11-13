# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/10/16
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
