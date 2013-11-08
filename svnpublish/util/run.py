# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/10/16
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import subprocess, sys

from svnpublish import api
from .struct import flattenlist

#------------------------------------------------------------------------------
def run(*cmd, **kwargs):
  '''keyword arguments can include: *env* and *input*'''
  cmd = [c for c in flattenlist(cmd) if c is not None]
  # todo: should i just pass **kwargs to Popen?
  try:
    p = subprocess.Popen(cmd,
                         stdin='input' in kwargs and subprocess.PIPE or None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=kwargs.get('env')
                         )
  except TypeError:
    raise
  if 'input' in kwargs:
    output, errput = p.communicate(kwargs.get('input'))
  else:
    output, errput = p.communicate()
  if p.returncode != 0:
    raise api.CommandFailed('command "%s" failed: %s' % (' '.join(cmd), errput))
  return output

#------------------------------------------------------------------------------
def runchk(config, *args, **kwargs):
  if config.dryrun:
    print >>sys.stderr, '[--] dryrun command: %s' \
          % (' '.join([a for a in flattenlist(args) if a is not None]),)
    return None
  return run(*args, **kwargs)


#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
