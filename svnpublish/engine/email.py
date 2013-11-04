# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  svnpublish.engine
# desc: emails recipients about changes to a repository
# auth: griffin <griffin@uberdev.org>
# date: 2009/09/05
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

from genemail.util import extractEmails
from svnpublish.util import autoresolve, asList

#------------------------------------------------------------------------------
def publish_email_dryrun(context):
  return publish_email(context)

#------------------------------------------------------------------------------
def publish_email(context):
  '''
  Configurable parameters:

  :Parameters:

  mailfrom : str, optional
  recipients : list(str), optional
  template : str, optional, default: 'engine-email/truncated'
  genemail : resolved-dict, optional, default: framework
  style : str, optional
  '''

  # todo: add `bcc` parameter, which is like `recipients` but does not
  #       list them to the 'to' line.

  # TODO: add 'lessc' mako filter...

  if not context.options.genemail:
    tpl = context.template or 'engine-email/truncated'
    context.logger.debug('using framework email manager template "%s"', tpl)
    eml = context.svnpub.genemail.newEmail(tpl)

  else:
    tpl = context.template
    context.logger.debug('using custom email manager template "%s"', tpl)
    eml = autoresolve(context.options.genemail).newEmail(tpl)

  mailfrom = context.mailfrom
  rcpts    = asList(context.recipients, None)

  if rcpts and not eml.hasHeader('to'):
    eml.setHeader('to', ', '.join(rcpts))

  eml['params']  = context
  eml['revinfo'] = context.revinfo
  eml['style']   = context.style

  if context.dryrun:
    context.logger.info('dry-run: commit-notification from %s to %s',
                        mailfrom, ', '.join(rcpts or []) or None)
    context.logger.debug('  subject: %s', eml.getSubject())
    context.logger.noise('raw SMTP email:')
    context.logger.noise(eml.getSmtpData())
    return

  eml.send(mailfrom=mailfrom, recipients=rcpts)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
