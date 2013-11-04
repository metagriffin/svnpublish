# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# desc: svnpublish exposed object APIs
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/04
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
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
