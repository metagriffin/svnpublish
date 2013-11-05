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
  def __init__(self, prune=True, sign=None, gpg_options=None):
    self.prune = prune
    self.sign  = sign
    self.gpg   = gnupg.GPG(**(gpg_options or dict()))

  #----------------------------------------------------------------------------
  def modify(self, mailfrom, recipients, data, *other):

    if not asset.isstr(data):
      hdritems = data.items()
      data = data.as_string()
      if not data.endswith('\n'):
        data += '\n'

    else:
      hdritems = email.message_from_string(data).items()

    if self.prune:
      keys = self.gpg.list_keys()
      recipients = list(set(recipients))
      for rcpt in recipients[:]:
        for key in keys:
          if rcpt in ','.join(key.get('uids', [])):
            break
        else:
          # TODO: the 'to' in the email should get updated as well...
          #         ==> from both the original email *AND* the encrypted email
          recipients.remove(rcpt)
          log.warning('recipient %s removed (not found in keys)', rcpt)

    data = self.gpg.encrypt(data, recipients, sign=self.sign, always_trust=True)
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
