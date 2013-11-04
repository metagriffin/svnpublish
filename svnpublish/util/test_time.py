# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: griffin <griffin@uberdev.org>
# date: 2011/06/02
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
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
