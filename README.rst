===================================
Automated Publishing for Subversion
===================================

Welcome to **svnpublish**, a tool to enable automated publishing (and
any other arbitrary commands to be executed) when updates are made to
a subversion version control repository.

Publishing configurations are tied to either the entire repository or
restricted to subdirectories, referred to as a ``publishing point`` in
svnpublish-speak.

.. warning::

  For installation, use ``easy_install``, not ``pip``! The latter is
  currently breaking pkg_resources' ability to load resources.


Project
=======

* Homepage: https://github.com/metagriffin/svnpublish
* Bugs: https://github.com/metagriffin/svnpublish/issues


TL;DR
=====

Install:

.. code-block:: bash

  $ easy_install svnpublish
  $ mkdir -p /etc/svnpublish
  $ svnpublish --init-options > /etc/svnpublish/myrepos.yaml

  # edit the self-documenting configuration file:
  $ vi /etc/svnpublish/myrepos.yaml

Put in your ``REPOSITORY/hooks/post-commit``:

.. code-block:: bash

  #!/bin/sh
  svnpublish --options /etc/svnpublish/myrepos.yaml "$@"

If running in asynchronous mode:

.. code-block:: bash

  TODO: show example of getting svnpublishd running


Overview
========

TODO: add docs


Global Configuration
====================

The best way to set the initial svnpublish options is to use the
``--init-options`` flag, which outputs a list of all available options
accompanied with documentation. The recommended approach is to create
a per-repository configuration in ``/etc/svnpublish/`` which can be
done as follows:

.. code-block:: bash

  $ sudo mkdir -p /etc/svnpublish
  $ svnpublish --init-options | sudo tee /etc/svnpublish/REPOSITORY.yaml > /dev/null
  $ sudo vi /etc/svnpublish/REPOSITORY.yaml

And then modifying all of the options as needed. At a minimum, the
following options should be set:

* admin
* label
* name
* reposUrl
* genemail.default.headers.from


Publishing Point Configuration
==============================

TODO: add docs

.. code-block:: yaml

  publish:

    ENGINE:

      ATTRIBUTE: VALUE


Example:

.. code-block:: yaml

  publish:

    # send an email notification
    - engine:       email
      mailfrom:     noreply@example.com
      recipients:
                    - user1@example.com
                    - user2@example.com

    # update an RSS (atom) feed
    - engine:       rss
      window:       50
      label:        Repository Feed
      output:       /var/www/rss/output.xml
      feedUrl:      https://svn.example.com/rss/output.xml

    # export the repository to the file system
    - engine:       export
      path:         /var/www/example.com
      fixate:
                    - { engine: fingerprint }
                    - { engine: fingerprint, path: htdocs/fingerprint }

    # export the repository to a remote host
    - engine:       export
      remote:       svnpublish@example.com
      keychain:     /home/svnpublish/.keychain
      path:         /var/www/example.com
      fixate:
                    - { engine: fingerprint }
                    - { engine: fingerprint, path: htdocs/fingerprint }


Encrypted Email
===============

SvnPublish can be configured to send PGP-encrypted email, which
protects the contents of the emails from being read by unintended
recipients. Follow the instructions in
https://pypi.python.org/pypi/genemail to setup a GPG-home directory,
then adjust the svnpublish "options.yaml" file to include the
PgpModifier. For example:

.. code-block:: yaml

  # ... other configurations ...

  genemail:
    modifier:
      class:   'genemail.PgpModifier'
      sign:    'noreply@example.com'
      gpg_options:
        gnupghome: '/path/to/gpghome'


(See ``svnpublish --init-options`` for details on the various
options available.)
