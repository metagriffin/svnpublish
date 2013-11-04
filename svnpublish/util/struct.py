# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/10/16
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

from asset import isstr, symbol

#------------------------------------------------------------------------------
def asList(value, defval=[]):
  if value is None:
    return defval
  if isinstance(value, (list, tuple)):
    return list(value)
  # todo: if isstr(value) return value.split()?...
  return [value,]

#------------------------------------------------------------------------------
def flattenlist(l, ltypes=(list, tuple)):
  ltype = type(l)
  l = list(l)
  i = 0
  while i < len(l):
    while isinstance(l[i], ltypes):
      if not l[i]:
        l.pop(i)
        i -= 1
        break
      else:
        l[i:i + 1] = l[i]
    i += 1
  return ltype(l)

#------------------------------------------------------------------------------
def autoresolve(obj):
  if isstr(obj):
    return obj
  if isinstance(obj, (list, tuple)):
    return [autoresolve(e) for e in obj]
  if not isinstance(obj, dict) or 'class' not in obj:
    return obj
  params = {k: autoresolve(v) for k, v in obj.items() if k != 'class'}
  return symbol(obj['class'])(**params)

#------------------------------------------------------------------------------
def flatten(obj):
  if not isinstance(obj, dict):
    return obj
  ret = dict()
  for key, val in obj.items():
    val = flatten(val)
    if isinstance(val, dict):
      for skey, sval in val.items():
        ret[key + '.' + skey] = sval
    else:
      ret[key] = val
  return ret

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
