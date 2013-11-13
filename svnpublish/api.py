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

#------------------------------------------------------------------------------
class FrameworkError(Exception):
  def __init__(self, value, cause=None, *args, **kw):
    super(FrameworkError, self).__init__(value, *args, **kw)
    self.cause = cause
class EngineLoadError(FrameworkError): pass
class CommandFailed(FrameworkError): pass
class IncompatibleSvnlookVersion(FrameworkError): pass
class UnknownConfigSource(FrameworkError): pass
class InvalidSvnlookDiff(FrameworkError): pass
class UnsupportedConfigOption(FrameworkError): pass
class UnknownUriScheme(FrameworkError): pass

#------------------------------------------------------------------------------
class ConfigSource(object):
  def __init__(self, svnpub):
    self.svnpub = svnpub
  def getConfig(self, root):
    raise NotImplementedError()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
