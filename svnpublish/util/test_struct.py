# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2011/06/02
# copy: (C) Copyright 2011-EOT metagriffin -- see LICENSE.txt
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
