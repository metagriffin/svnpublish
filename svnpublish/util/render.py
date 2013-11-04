# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/10/21
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
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
