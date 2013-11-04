# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: griffin <griffin@uberdev.org>
# date: 2011/06/02
# copy: (C) CopyLoose 2009 UberDev <hardcore@uberdev.org>, No Rights Reserved.
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
