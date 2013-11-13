#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2010/12/21
# copy: (C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
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

import os, sys, setuptools
from setuptools import setup, find_packages

# require python 2.7+
if sys.hexversion < 0x02070000:
  raise RuntimeError('This package requires python 2.7 or better')

heredir = os.path.abspath(os.path.dirname(__file__))
def read(*parts, **kw):
  try:    return open(os.path.join(heredir, *parts)).read()
  except: return kw.get('default', '')

test_dependencies = [
  'nose                 >= 1.3.0',
  'coverage             >= 3.6',
  'fso                  >= 0.1.5',
  'pxml                 >= 0.2.9',
  ]

dependencies = [
  'distribute           >= 0.6.24',
  'PyYAML               >= 3.10',
  'six                  >= 1.4.1',
  #'TemplateAlchemy      >= 0.1.20',
  'genemail             >= 0.1.10',
  'lesscpy              >= 0.9j',
  'aadict               >= 0.2.0',
  'globre               >= 0.0.5',
  'asset                >= 0.0.4',
  ]

extras_dependencies = {
  'genshic'             : 'genshi            >= 0.6',
  'pgpemail'            : 'genemail[pgp]     >= 1.2.3',
  ## 'jinja2c'             : 'jinja2            >= 2.7.1',
  ## 'chameleonc'          : 'chameleon         >= 2.12',
  }

entrypoints = {
  'console_scripts': [
    'svnpublish         = svnpublish.cli:main',
    'svnpublishd        = svnpublish.async:main',
    ],
  }

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Environment :: Console',
  'Intended Audience :: Developers',
  'Intended Audience :: Information Technology',
  'Intended Audience :: System Administrators',
  'Natural Language :: English',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Internet :: WWW/HTTP :: Site Management',
  'Topic :: Other/Nonlisted Topic',
  'Topic :: Software Development',
  'Topic :: Software Development :: Libraries :: Python Modules',
  'Topic :: Software Development :: Version Control',
  'Topic :: Utilities',
  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
  ]

setup(
  name                  = 'svnpublish',
  version               = read('VERSION.txt', default='0.0.1').strip(),
  description           = 'Enables powerful automation from a subversion repository.',
  long_description      = read('README.rst'),
  classifiers           = classifiers,
  author                = 'metagriffin',
  author_email          = 'mg.pypi@uberdev.org',
  url                   = 'http://github.com/metagriffin/svnpublish',
  keywords              = 'svn subversion publish automation actions deploy test testing',
  packages              = find_packages(),
  platforms             = ['any'],
  namespace_packages    = ['svnpublish'],
  include_package_data  = True,
  zip_safe              = True,
  install_requires      = dependencies,
  extras_require        = extras_dependencies,
  tests_require         = test_dependencies,
  test_suite            = 'svnpublish',
  entry_points          = entrypoints,
  license               = 'GPLv3+',
  )

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
