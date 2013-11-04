# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: echos the changes to stderr (really, just for debugging, eh?)
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/05
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def publish_echo_dryrun(params):
  return publish_echo(params)

#------------------------------------------------------------------------------
def publish_echo(params):
  params.logger.info('publishing point "%s":', params.root)
  params.logger.info('  repository:    "%s"', params.repository)
  params.logger.info('  revision:      %s', params.revision)
  params.logger.info('  admin:         %s', ', '.join(params.admin))
  params.logger.debug('  changes:')
  for entry in params.revinfo.changes:
    params.logger.debug('    %s', str(entry))
  params.logger.drivel('  diff:')
  params.logger.drivel('    ' + '\n    '.join(params.revinfo.diff.split('\n')))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
