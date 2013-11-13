# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2009/09/05
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
