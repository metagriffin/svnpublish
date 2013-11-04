===================================
Automated Publishing for Subversion
===================================

Welcome to **svnpublish**, a tool to enable automated publishing (and
any other arbitrary commands to be executed) when updates are made to
a subversion version control repository.

Publishing configurations are tied to either the entire repository or
restricted to subdirectories, referred to as a ``publishing point`` in
svnpublish-speak.


TL;DR
=====

Install:

.. code-block:: bash

  $ pip install svnpublish
  $ mkdir -p /etc/svnpublish
  $ svnpublish --init-options > /etc/svnpublish/myrepos.yaml

  # edit the configuration file
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

    - engine:       email
      mailfrom:     noreply@example.com
      recipients:
                    - user1@example.com
                    - user2@example.com

    - engine:       rss
      window:       50
      label:        Repository Feed
      output:       /var/www/rss/output.xml
      feedUrl:      https://svn.example.com/rss/output.xml

    - engine:       export
      path:         /var/www/example.com
      fixate:
                    - { engine: fingerprint }
                    - { engine: fingerprint, path: htdocs/fingerprint }

    - engine:       export
      remote:       svnpublish@example.com
      keychain:     /home/svnpublish/.keychain
      path:         /var/www/example.com
      fixate:
                    - { engine: fingerprint }
                    - { engine: fingerprint, path: htdocs/fingerprint }
