=========
ChangeLog
=========


v2.12
=====

* Fixed shell execution when exporting to remote targets


v2.0.11
=======

* Fixed the "pip" installation issues (by removing namespace support
  and forcing version 0.9.10 of cssutils)
* Set email "Date" header to commit-date instead of generation-date


v2.0.10
=======

* Added HTML diff colorization support to email engine


v2.0.9
======

* Added more logging and preambles
* Added version fingerprinting to outbound emails
* Converted to GPLv3+


v2.0.8
======

* Added "--init-service" option to svnpublishd
* Cleaned up default options documentation
* Moved to genemail-based PGP
* Added "--version" command-line display option
* Fixed export/fingerprint "path" option defaulting bug


v2.0.5
======

* Added asynchronous operation mode (via 'svnpublishd' daemon)


v2.0.3
======

* Added outbound GPG email encryption support
* Corrected packaging (added missing "res" and "test" files)


v2.0.0
======

* Ported to GitHub
* Converted to use genemail_ and TemplateAlchemy_
* Renamed "genshi-compile" engine to "genshic"
* Refactored CLI option loading


.. _genemail: https://pypi.python.org/pypi/genemail
.. _TemplateAlchemy: https://pypi.python.org/pypi/TemplateAlchemy
