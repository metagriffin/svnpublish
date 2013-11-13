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
