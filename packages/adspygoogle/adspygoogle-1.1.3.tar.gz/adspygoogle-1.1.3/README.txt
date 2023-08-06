===========================================
The Google Ads APIs Python Client Libraries
===========================================

The Google Ads APIs Python Client Libraries support the following products:

* AdWords API Python Client Library v15.11.1
* DoubleClick for Advertisers API Python Client Library v2.4.1
* DFP API Python Client Library v9.9.0

You can find more information about the Google Ads Python Client Libraries
`here <https://code.google.com/p/google-api-ads-python/>`_.

Installation
============

You have two options for installing the Ads Python Client Libraries:

* Install with a tool such as pip::

  $ sudo pip install adspygoogle

* Install manually after downloading and extracting the tarball::

  $ sudo python setup.py install

Examples and Configuration Scripts
==================================

This package only provides the core components necessary to use the client
libraries. If you would like to obtain example code for any of the included
client libraries, you can find it on our
`downloads page <https://code.google.com/p/google-api-ads-python/downloads/list>`_.

Known Issues
============

* By default, the PyXML dependency is currently incompatible with Ubuntu 13.04.
  A consequence of this is that the installation of adspygoogle will fail.
  For now, you can use the work-around described in
  `this bug <https://bugs.launchpad.net/ubuntu/+source/python2.7/+bug/1238244/>`_.

Contact Us
==========

Do you have an issue using the Ads Python Client Libraries? Or perhaps some
feedback for how we can improve them? Feel free to let us know on our
`issue tracker <https://code.google.com/p/google-api-ads-python/issues/list>`_.