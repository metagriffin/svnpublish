=========
ChangeLog
=========


2.0.8
=====

* Added "--init-service" option to svnpublishd
* Cleaned up default options documentation
* Moved to genemail-based PGP
* Added "--version" command-line display option
* Fixed export/fingerprint "path" option defaulting bug


2.0.5
=====

* Added asynchronous operation mode (via 'svnpublishd' daemon)


2.0.3
=====

* Added outbound GPG email encryption support
* Corrected packaging (added missing "res" and "test" files)


2.0.0
=====

* Ported to GitHub
* Converted to use genemail_ and TemplateAlchemy_
* Renamed "genshi-compile" engine to "genshic"
* Refactored CLI option loading


.. _genemail: https://pypi.python.org/pypi/genemail
.. _TemplateAlchemy: https://pypi.python.org/pypi/TemplateAlchemy
