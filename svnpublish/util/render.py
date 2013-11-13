# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2013/10/21
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

from ..i18n import _

#------------------------------------------------------------------------------
# todo: there must be a library for this...
# todo: show exactly 2 significant digits, ie 3276 bytes should render as
#       "3.2 KB" instead of "3.20 KB" and 32760 bytes => "32 KB"
def size2str(size):
  if size < 1024:
    return str(size) + ' bytes'
  size /= 1024.0
  if size < 1024:
    return '%.2f KB' % (size,)
  size /= 1024.0
  if size < 1024:
    return '%.2f MB' % (size,)
  size /= 1024.0
  if size < 1024:
    return '%.2f GB' % (size,)
  size /= 1024.0
  if size < 1024:
    return '%.2f TB' % (size,)
  size /= 1024.0
  return '%.2f PB' % (size,)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
