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

import unittest, yaml
from aadict import aadict

from svnpublish import framework
from .config import mergeOptions

#------------------------------------------------------------------------------
class TestConfig(unittest.TestCase):

  #----------------------------------------------------------------------------
  def test_mergeOptions(self):
    base     = aadict(yaml.load(framework.defaultOptions))
    override = yaml.load('reposUrl: https://svn.example.com/repos\n')
    options  = mergeOptions(base, override)
    self.assertEqual(None, base.reposUrl)
    self.assertEqual('https://svn.example.com/repos', options.reposUrl)

  #----------------------------------------------------------------------------
  def test_mergeOptions_nulldeletes(self):
    base     = aadict.d2ar(yaml.load(framework.defaultOptions))
    override = yaml.load('genemail: {default: null}')
    options  = mergeOptions(base, override)
    self.assertNotEqual(None, base.genemail.default)
    self.assertEqual(None, options.genemail.default)
    self.assertIn('default', base.genemail)
    self.assertNotIn('default', options.genemail)


#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
