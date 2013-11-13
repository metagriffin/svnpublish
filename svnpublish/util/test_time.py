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

from __future__ import absolute_import

import unittest, time

from ..test_helper import stoptime, unstoptime, StopTimeMixin
from .time import now

#------------------------------------------------------------------------------
class TestTime(unittest.TestCase):
  def test_now_override(self):
    # this assumes time.time() has *at least* 0.1s precision...
    t1 = now()
    time.sleep(0.1)
    t2 = now()
    self.assertNotEqual(t1, t2)
    ret = stoptime(1234)
    self.assertEqual(ret, 1234.0)
    self.assertEqual(now(), 1234)
    time.sleep(0.1)
    self.assertEqual(now(), 1234)
    unstoptime()
    self.assertNotEqual(now(), 1234)
    t1 = now()
    time.sleep(0.1)
    t2 = now()
    self.assertNotEqual(t1, t2)

#------------------------------------------------------------------------------
class TestTimeMixin(StopTimeMixin, unittest.TestCase):
  def setUp(self):
    super(TestTimeMixin, self).setUp()
    self.randomattr = 'slartibartfast'
  def test_mixin(self):
    t1 = now()
    time.sleep(0.1)
    t2 = now()
    self.assertEqual(t1, t2)
    self.assertEqual(self.stoppedtime, t1)
    self.assertIsNotNone(self.stoppedtime)
    self.assertEqual(self.randomattr, 'slartibartfast')

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
