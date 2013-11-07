# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <metagriffin@uberdev.org>
# date: 2013/11/04
# copy: (C) CopyLoose 2013 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

# TODO: this implements PGP/MIME (RFC 3156), add support for:
#         - inline-PGP
#         - S/MIME

# TODO: look into:
#   - http://www.ietf.org/rfc/rfc4880.txt
#   - https://www.enigmail.net/documentation/features.php
#   - http://sites.inka.de/tesla/gpgrelay.html

# TODO: add a setting for a key server, and if the recipient is not
#       known, look them up in there... *AWESOME* :)

from __future__ import absolute_import

import re, logging, genemail, gnupg, asset, email

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class EncryptModifier(genemail.Modifier):

  #----------------------------------------------------------------------------
  def __init__(self, prune_keys=True, prune_recipients=False,
               sign=None, add_key='sign-key', gpg_options=None):
    self.kprune  = prune_keys
    self.rprune  = prune_recipients
    self.sign    = sign
    self.addkeys = add_key
    if self.addkeys is not None:
      if asset.isstr(self.addkeys):
        self.addkeys = [self.addkeys]
      self.addkeys = list(set(self.addkeys))
      if 'sign-key' in self.addkeys:
        self.addkeys.remove('sign-key')
        if self.sign is not None:
          self.addkeys.append(self.sign)
    self.gpg    = gnupg.GPG(**(gpg_options or dict()))

  #----------------------------------------------------------------------------
  def modify(self, mailfrom, recipients, data, *other):

    rcptlist = list(set(recipients))

    if self.kprune:
      keys = self.gpg.list_keys()
      for rcpt in rcptlist[:]:
        for key in keys:
          if rcpt in ','.join(key.get('uids', [])):
            break
        else:
          # TODO: the 'to' in the email should get updated as well...
          #         ==> from both the original email *AND* the encrypted email
          rcptlist.remove(rcpt)
          log.warning('recipient %s removed (not found in keys)', rcpt)

    if self.rprune:
      recipients = rcptlist[:]

    if self.addkeys:
      rcptlist = list(set(rcptlist + self.addkeys))

    if not asset.isstr(data):
      hdritems = data.items()
      data = data.as_string()
      if not data.endswith('\n'):
        data += '\n'

    else:
      hdritems = email.message_from_string(data).items()

    data = self.gpg.encrypt(data, rcptlist, sign=self.sign, always_trust=True)
    if not data.ok:
      raise ValueError('Encryption failed: ' + data.status)

    edata = email.MIMEMultipart.MIMEMultipart(
      'encrypted', protocol='application/pgp-encrypted')

    params = email.MIMENonMultipart.MIMENonMultipart('application', 'pgp-encrypted')
    params.set_payload('Version: 1\n')
    edata.attach(params)

    payload = email.MIMENonMultipart.MIMENonMultipart('application', 'octet-stream')
    payload.set_payload(str(data))
    edata.attach(payload)

    for key, value in hdritems:
      if key.lower() in ('content-type', 'mime-version'):
        continue
      edata.add_header(key, value)

    return (mailfrom, recipients, edata) + other

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
