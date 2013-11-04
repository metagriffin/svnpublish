# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: griffin <griffin@uberdev.org>
# date: 2011/06/02
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

import unittest

from .struct import flatten

#------------------------------------------------------------------------------
class TestStruct(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_flatten(self):
    src = dict(foo=dict(bar=dict(zig='zag', moo=3), baz='zog'), bingo='star')
    chk = {
      'foo.bar.zig': 'zag',
      'foo.bar.moo': 3,
      'foo.baz': 'zog',
      'bingo': 'star',
      }
    self.assertEqual(flatten(src), chk)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
