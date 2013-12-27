===================================
Automated Publishing for Subversion
===================================

Welcome to **svnpublish**, a tool to enable automated publishing (and
any other arbitrary commands to be executed) when updates are made to
a subversion version control repository.

Publishing configurations are tied to either the entire repository or
restricted to subdirectories, referred to as a ``publishing point`` in
svnpublish-speak.


Project
=======

* Homepage: https://github.com/metagriffin/svnpublish
* Bugs: https://github.com/metagriffin/svnpublish/issues


TL;DR
=====

Install:

.. code-block:: bash

  $ pip install svnpublish
  $ mkdir -p /etc/svnpublish
  $ svnpublish --init-options > /etc/svnpublish/myrepos.yaml

  # edit the self-documenting configuration file:
  $ vi /etc/svnpublish/myrepos.yaml

Put in your ``REPOSITORY/hooks/post-commit``:

.. code-block:: bash

  #!/bin/sh
  svnpublish --options /etc/svnpublish/myrepos.yaml "$@"

If running in asynchronous mode (recommended):

.. code-block:: bash

  $ apt-get install daemontools-run

  # create the service directory with the user:group that runs svnpublish
  $ svnpublishd --init-service --service-dir /etc/service/svnpublishd --user www-data:www-data

  # review the output and adjust the service configuration:
  $ vi /etc/service/svnpublishd/run /etc/service/svnpublishd/log/run

  # grant the user running svnpublish access to HUP the service
  # (this assumes that "#includedir /etc/sudoers.d" is in "/etc/sudoers.d",
  #  that the user is www-data, and that svc is located in /usr/bin)
  $ echo "www-data ALL = NOPASSWD: /usr/bin/svc -h /etc/service/svnpublishd" > /etc/sudoers.d/svnpublishd
  $ chmod 440 /etc/sudoers.d/svnpublishd

  # start the service
  $ rm -f /etc/service/svnpublishd/down
  $ svc -u /etc/service/svnpublishd

Then add the "--async" option to svnpublish (making sure that the
`serviceDir` option is set correctly in the svnpublish "options.yaml"
file). Extending the above example, the new post-commit hook should
look something like:

.. code-block:: bash

  #!/bin/sh
  svnpublish --options /etc/svnpublish/myrepos.yaml --async "$@"

NOTE: it is recommended to move the log directory to a more
system-appropriate location -- see
``/etc/service/svnpublishd/log/run``.

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


Asynchronous Operation
======================

Svnpublish can run in asynchronous mode (the recommended approach),
which means that commits happen quickly, and an asynchronous process
then takes care of executing the publishing. This asynchronous
process, ``svnpublishd``, has been geared at being run by DJB's
`daemontools <http://cr.yp.to/daemontools.html>`_. On debian-based
systems, daemontools can be easily installed with:

.. code-block:: bash

  $ apt-get install daemontools-run

The svnpublishd service directory can be created automatically by a
call to ``svnpublishd --init-service OPTIONS``, which creates all of
the directories, "run" scripts, and default logging options necessary
to run svnpublishd, tailored for the specified user:group that
svnpublish runs as. It is important to ensure this user:group setting
is correct, as otherwise svnpublish and svnpublishd cannot
communicate. The user:group that svnpublish runs as is usually the
owner of the subversion repository. For example, if your svnpublish
runs as www-data:www-data, then something like this should work:

.. code-block:: bash

  $ svnpublishd --init-service --service-dir /etc/service/svnpublishd --user www-data:www-data

Copyright Notice
================

This software is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/.

\(C) Copyright 2013-EOT metagriffin -- see LICENSE.txt
