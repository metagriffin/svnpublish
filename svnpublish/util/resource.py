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

# TODO: replace with `asset` package when available...

import os, re, pkg_resources

from .. import api

#------------------------------------------------------------------------------
def getResourceStream(name):
  return pkg_resources.resource_stream(__name__, '../res/' + name)

#------------------------------------------------------------------------------
def getResourceString(name):
  return pkg_resources.resource_string(__name__, '../res/' + name)

#------------------------------------------------------------------------------
def str2sym(name):
  # todo: what about ensuring that the first char is alphabetic?
  return re.sub('[^a-zA-Z0-9_]+', '_', name)

#------------------------------------------------------------------------------
def getUriContent(uri, context=None, defaultScheme='file'):
  # TODO: replace this with TemplateAlchemy?...
  if uri.startswith('svn:'):
    # tbd: perhaps support non-local svn (via 'svn://')?...
    uri = uri[4:]
    if not uri.startswith('/') and context.svndir is not None:
      uri = os.path.join(context.svndir, uri)
    return context.svnrev.svnlook('cat', uri)
  if uri.startswith('data:'):
    ctype, data = uri[5:].split(';', 1)
    enc, data = data.split(',', 1)
    return data.decode(enc)
  if uri.startswith('svnpublish-res:'):
    return getResourceStream(uri[15:])
  # TBD: i should use urllib2 here...
  if uri.startswith('file://'):
    return open(uri[7:], 'rb')
  if defaultScheme == 'file':
    return open(uri, 'rb')
  raise api.UnknownUriScheme(uri)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
